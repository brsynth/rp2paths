"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from os import path as os_path
from module import module


files = {
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000003.svg'):   'c7e963be69384a7e1699f97bdbb466fe7f75c6c48e43f26ba34e868af1746ebd16e51d930d8311abb2dcb6569b2290e13ed37b8707cb2578ca1eaf2218518813',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000005.svg'):   '407b70151cb70e76a1a6589ca7a101c4466b9c086ebdd24386487ec3e6bc4cfe116272eab43c84dd6ee7a2f7d321f65e338177f9ebc4bf623be7440e86aa465e',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000007.svg'):   '1d1732a3c33efdfa64160c536620e427677d55acf1ca7a4a49eb7127e8869a68ea7d51959c06fabc6430190bbeab672644c0771592842cad5eba922e0181aa49',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000008.svg'):   '50125a23542af33952733057e5c8a40f9e53f8bb6ecbc73e6884f2ec050958cf373a68e51ed38c87e96f27016802f8c9c3135604145abc2d1402349a40bcf122',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000009.svg'):   '20ed35dd2b732cc9379082455c5cedc07e56fa33a298597a225fdb6c7383269677cddd40bdcc3f9453fb7a9c49e411727ce38cceb98d4ba9f620404c244c5e65',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000010.svg'):   'e99da8260fc1240917be706c5f013041afa0f7597c5deae3622fc1208ae62a9ced92385a0078bf66d48cc264fb4b25fa26340919fd462caadd14ab46a03679db',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000015.svg'):   'ea302fcfc7becdf0d1525220aa4f8f4d08eca05df4ac15456bca77ff7fa8b8ac47dcf32677e30475383069f57102f5ea079e0466c5fdd1858e72da3d34ed3d1d',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000020.svg'):   '9f561a488d3225ef6fb56c8ddf87efacd3ebb90d9eee0aa0a7678539b03d562d5c862c046ab7dca230f7c7c04cb3fa60edfd28e3164dfc4ce870c0a5bfb5390a',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000025.svg'):   '2bdb15c8581ca01ff2bc21ee297ad8c5fad169c4c5bfe1c74c34ddf4adeabd60c38df483c3d883238278e3f376b8d149f6146eb680cfb8adcdd596a1a38dd3cb',
        os_path.join(module.args.outdir, module.args.imgdir+'/CMPD_0000000028.svg'):   '98b3af42af0369a32f12b7d58102322aed842ac622a03979a5161d9b9da2fde293a1d6717a82f77308edfd590637183bf7c540bd4bd5ab8169019943d5bdcf25',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM1.svg'):             'cbacf47fc19c7ed52404d37ba13d7b10030de202c68e4f5313783c5b9b5896bc37faabb538bebfdd211ee7638c958b2cb4e4e60439f2fc664a92a4ffec4ebb87',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM10.svg'):            '8abe849e6d6eb2eb195dffb5f28aca6015eef7299e20d9fdbf1ded62a57e04a6692c06080faf67f05f2c06c6d3d05c7c2bae8cca3a66cf837c19624398c56ec1',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM11.svg'):            '41cc1d57e91cd9003d32fe3032129aa3d4d55df02c1b089efdb04587035c049c3a01216b1668444237603aa7708930011d0253dc8c80a2799ff374083eb585ac',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM1132.svg'):          '0ed590e6da7787a4e61fc1f8436a0c00001f78e7a655e20ec6583a223df71f9c5a9a0848fc0b2ce041f64fdd154a926fd7b4e57d5ed7ac1f4974a940060fb70d',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM12.svg'):            '92cee963745d754dbfdd7422ac1f9aad1d66f4b7a46d4ff100e58b871a98d6fcdb2c4b9cb2c172133e7f8ac0369477c35032ed200217a62e4f95d479aa64a61c',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM164.svg'):           'f6f5692d9ba329e5e73176e2962afebbb1cb29c63069151c637114cd498d414241772654aa229d7fa27fe2113c14580dd173354d21ee6bde7186e3c57cb06ebb',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM188.svg'):           '46162377952f698cd40086e7cea2902c6dc8af6489b3a9577812486b7fa570d67bd7faec044edab4eedbecaebd394eef8275b67748ef9838dec6ee02cf34c7cd',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM2.svg'):             '3bc79953606825d8bfd9f71612a924441feeb36b6e77a088183feb1863c82b13f4e3a600aacc472b2e517d9f792ac4974f7eb0328db5db8fd4ec37bb1a8000c9',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM25.svg'):            '59227b7942c6452c51bccab73ef78ac68e1785756ed4a89554499c83c6d8987293007a5709fda083d8f048f32391f6b8b1eebdc4947b668e42c957608417ce94',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM337.svg'):           '35d9010bc836ad4fc0ee0408251b451f930ec4a4e0d7dae6956d0e222cfef8d5d3af03fa57163fe4a0db5d59be6e36e32dba192b2ad13d201fa20bd303f967bd',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM4.svg'):             '71d5f266dee3b6aa8b3454781992e3ba2e0df009b010df0d9a1f5c65377bc421d19de68893bf34dc637d1d391fc19411dabe556f5f9ee4dde8011f15822bf6f7',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM421.svg'):           'd61932d92571cc74f140f02a04ac6f1ee618a4f96a57f8f6c313547f5203baf42b633932b4ea5aeefe0ffb94e9ec7fb5adb3a3d7b15a2b388cbc5ec928108f98',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM438.svg'):           '7a15de421ee6248b2d13dcda96579b4feec5ed5d2180f666675a4486e742ac038d5bb773a792c0e5e729c95372dd3b3c1d6c077eb5ec8eaf4dfbae331dc24f0e',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM455.svg'):           'a191cbf214f36c90a34b7a31f2090abfd7c8adeaf101cdb423b4fb5a1ad0796574a76322c832d8188e0ed32247383752b4d31c94663e49e5c6ad43c75def72d2',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM473.svg'):           '62351971223161e4b6c4996f9745b7599f2d2d4e5b671d23ab016c2b95edb2560bc196ab5e6b9eb07e087f445eba2cf2b964d63f831c8ff24c9c8964bc09d707',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM497.svg'):           '20d0c1cc922c9009fd378b31500e5f3c0c2199b22123d82b615995d32e1f4823c7c244121e932a14ab0bd1de748864381813409306524f4e6b4ce61aef817ef4',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM6.svg'):             '17bdf2115eb6ccbcadf293c840cff568104559d1691948d32dd72aa063caf1c25c54e7292d29b2a4a1bbd45de94897190103dc9c1faeb93010e87064842b641b',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM611.svg'):           '0878330f4ceb59cfd0aa37ccf5fd38d49f2ff7e03b0d7d7d9271f63014ca5ac494de4abff32047ca53658c93081416bdea551ea7cdc584d240b7b67c95068fcb',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM76.svg'):            '63075c05dc339d8ad4bc173dbf69b6365e06cd61c096970ca1ecfdca2a0f9c4826627c16252d60409c2a677656e1542ab0c24b84a33571877298ff3fd1fc1871',
        os_path.join(module.args.outdir, module.args.imgdir+'/MNXM799.svg'):           '0ec62e7302592a802ac20b1fb230568c08c14783ed4813d7c696042719310b6e4e6abfbb0cded359a183d3be3234a7fb44101ca45346b2a8f254101ce0a17129',
        os_path.join(module.args.outdir, module.args.imgdir+'/TARGET_0000000001.svg'): '3714638da1b28944117246ccb02dd65b9abd2a871c0463884c68d651ff84675718593a07942aea92894d928243b57dc006ae4aadf6243ffb7022874dc9af10bf',
}
files = list(files.items())
# preexec_func_names = legacy_preexec + ['filter']
parent_test = 'filter'

class Test_Img(module):
    __test__ = True

    func_name = 'img'
    files = files

    def _check(self):
        self._check_files_exist()
