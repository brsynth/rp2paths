import pandas as pd
import argparse
import logging

def parse_labels(label_string, logger = logging.getLogger(__name__)):
    """
    Parse a single-line label file (space-separated, quoted labels).
    """
    if logger:
        logger.debug("Parsing label string.")
    return [lab.strip('"').strip() for lab in label_string.strip().split() if lab.strip()]

def read_inputs(mat_file, react_file, comp_file, logger = logging.getLogger(__name__)):
    """
    Read the stoichiometry matrix, reaction labels, and compound labels from input files.
    """
    if logger:
        logger.info(f"Reading reaction labels from {react_file}")
    with open(react_file, "r", encoding="utf-8") as f:
        react_content = f.read()
    if logger:
        logger.info(f"Reading compound labels from {comp_file}")
    with open(comp_file, "r", encoding="utf-8") as f:
        comp_content = f.read()
    reactions = parse_labels(react_content, logger)
    compounds = parse_labels(comp_content, logger)
    if logger:
        logger.info(f"Reading stoichiometry matrix from {mat_file}")
    stoich_mat = pd.read_csv(mat_file, sep="\t", header=None)
    stoich_mat.index = compounds
    stoich_mat.columns = reactions
    return stoich_mat, reactions, compounds

def build_reaction_dicts(stoich_mat, reactions, logger = logging.getLogger(__name__)):
    """
    Build dictionaries mapping each reaction to its substrates and products.
    """
    if logger:
        logger.info("Building reaction dictionaries.")
    substrates2reactions = {}
    reaction2products = {}
    for rxn in reactions:
        col = stoich_mat[rxn]
        substrates = [cmpd for cmpd, v in col.items() if v < 0]
        products  = [cmpd for cmpd, v in col.items() if v > 0]
        for sub in substrates:
            if sub not in substrates2reactions:
                substrates2reactions[sub] = []
            substrates2reactions[sub].append(rxn)
        reaction2products[rxn] = products
    return substrates2reactions, reaction2products

def enumerate_longest_paths(
    start_cmpd,
    substrates2reactions,
    reaction2products,
    max_depth=0,  # 0 means unlimited depth
    max_paths=0,  # 0 means unlimited paths
    logger = logging.getLogger(__name__)
):
    """
    Enumerate all longest paths (i.e., those that cannot be further extended)
    starting from the specified compound.
    """
    all_paths = []

    def dfs(current_cmpd, current_path, depth):
        if (max_depth > 0 and depth >= max_depth) or (current_cmpd not in substrates2reactions):
            if current_path not in all_paths:
                all_paths.append(current_path)
                logger.debug(f"Path {len(all_paths)}: {start_cmpd}, " + " -> ".join([f"({step})" for step in current_path]))
            if max_paths > 0 and len(all_paths) >= max_paths:
                logger.info(f"Reached maximum number of paths ({max_paths}). Stopping enumeration.")
                # exit(0)
            return

        for rxn in substrates2reactions[current_cmpd]:
            products = reaction2products[rxn]
            for product in products:
                # Avoid cycles by checking if the current reaction is already in the path
                if rxn not in current_path:
                    dfs(product, current_path + [rxn], depth + 1)

    dfs(start_cmpd, [], 0)
    return all_paths


# main function called from code with all arguments and parameters
def enumerate(
    mat_file,
    react_file,
    comp_file,
    start_cmpd,
    max_depth = 0,  # 0 means unlimited depth
    max_paths = 0,  # 0 means unlimited paths
    output_file = None,
    logger = logging.getLogger(__name__)
):
    logger.info("Reading input files...")
    stoich_mat, reactions, compounds = read_inputs(mat_file, react_file, comp_file, logger)
    logger.info(f"Number of compounds: {len(compounds)}")
    logger.debug(f"Compounds: {compounds}")
    logger.info(f"Number of reactions: {len(reactions)}")
    logger.debug(f"Reactions: {reactions}")
    logger.debug(f"Stoichiometry matrix:\n{stoich_mat}")

    # Invert the reactions in the stoichiometry matrix,
    # i.e. multiply by -1 to get the correct direction
    # stoich_mat = stoich_mat.map(lambda x: -x if x < 0 else x)

    # Add brackets to fit the expected format
    start_cmpd = f"[{start_cmpd}]"
    if start_cmpd not in compounds:
        logger.error(f"Starting compound {start_cmpd} not found in compounds list!")
        raise ValueError(f"Starting compound {start_cmpd} not found in compounds list!")

    logger.info("Building reaction graphs...")
    substrates2reactions, reaction2products = build_reaction_dicts(stoich_mat, reactions, logger)

    logger.info(f"Enumerating longest paths from {start_cmpd}...")
    paths = enumerate_longest_paths(
        start_cmpd,
        substrates2reactions,
        reaction2products,
        max_depth=max_depth,
        max_paths=max_paths,
        logger=logger
    )

    logger.info(f"Found {len(paths)} maximal-length paths.")
    # Write output into a 0/1 matrix where
    # lines are pathways, and
    # columns are reaction indices in reactions list
    if output_file:
        logger.info(f"Writing output to {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            # f.write("\t".join(reactions) + "\n")
            for path in paths:
                line = ["1" if rxn in path else "0" for rxn in reactions]
                line[-1] = "1"
                f.write("".join(line) + "\n")
    else:
        for path in paths:
            line = ["1" if rxn in path else "0" for rxn in reactions]
            line[-1] = "1"
            print("".join(line) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Enumerate all longest metabolic pathways from a given starting compound.")
    parser.add_argument("--mat", required=True, help="Path to the stoichiometry matrix file (tab-separated, no header)")
    parser.add_argument("--react", required=True, help="Path to the reactions label file")
    parser.add_argument("--comp", required=True, help="Path to the compounds label file")
    parser.add_argument("--start", required=True, help="Starting compound (e.g. TARGET_0000000001)")
    parser.add_argument("--max_depth", type=int, default=0, help="Optional: Maximum depth for path search, 0 (default) for \
        unlimited number of steps.")
    parser.add_argument("--max_paths", type=int, default=0, help="Optional: Maximum number of unique paths to enumerate, 0 \
        (default) for unlimited paths.")
    parser.add_argument("--output", default=None, help="Optional: Output file to save the paths (default: print to stdout)")
    parser.add_argument("--loglevel", default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    # Setup logger
    logger = logging.getLogger("rp2paths.enumerate")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, args.loglevel.upper(), logging.INFO))

    enumerate(
        mat_file=args.mat,
        react_file=args.react,
        comp_file=args.comp,
        start_cmpd=args.start,
        max_depth=args.max_depth,
        max_paths=args.max_paths,
        output_file=args.output,
        logger=logger
    )


if __name__ == "__main__":
    main()