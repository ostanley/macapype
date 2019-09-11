

from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    TraitedSpec)
from nipype.interfaces.base import traits, File


# AtlasBREX
class AtlasBREXInputSpec(CommandLineInputSpec):

    script_atlas_BREX = File(
        exists=True,
        desc='atlasBREX script',
        mandatory=True, position=0, argstr="%s")

    NMT_SS_file = File(
        exists=True,
        desc='Skullstriped version of the template',
        mandatory=True, position=1, argstr="-b %s")

    NMT_file = File(
        exists=True,
        desc='template img',
        mandatory=True, position=2, argstr="-nb %s")

    t1_restored_file = File(
        exists=True,
        desc='T1 image to map',
        mandatory=True, position=3, argstr="-h %s")

    f = traits.Float(
        0.5, usedefault=True, desc='f', position=4, argstr="-f %f",
        mandatory=True)

    reg = traits.Enum(
        1,0,2,3, usedefault=True, desc="Method: 0 = FNIRT w/ bending, \
            1 (default) = FNIRT membrane-energy regularization, \
            2 = ANTs/SyN w/, \
            3 = w/o N4Bias",
        position=5, argstr="-reg %d", mandatory=True)

    w = traits.String(
        "10,10,10", usedefault=True, desc="w", position=6, argstr="-w %s",
        mandatory=True)

    msk = traits.String(
        "a,0,0", usedefault=True, desc="msk", position=7, argstr="-msk %s",
        mandatory=True)


class AtlasBREXOutputSpec(TraitedSpec):

    brain_file = File(
        exists=True,
        desc="extracted brain from atlas_brex")


class AtlasBREX(CommandLine):
    """
    Description:
        Atlas based BrainExtraction


    Inputs:

        script_atlas_BREX:
        type = File, exists=True, desc='atlasBREX script',,
            mandatory=True, position=0, argstr="%s"

        NMT_SS_file:
        type = File, exists=True,
        desc='Skullstriped version of the template',
            mandatory=True, position=1, argstr="-b %s"

        NMT_file:
        type = File, exists=True, desc='template img',
        mandatory=True, position=2, argstr="-nb %s"

        t1_restored_file:
        type = File, exists=True, desc='T1 image to map',
            mandatory=True, position=3, argstr="-h %s"

        f:
        type = Float, default = 0.5, usedefault=True, desc='f', position=4,
        argstr="-f %f", mandatory=True

        reg : type = Enum, default = 1,0,2,3, usedefault=True,
        desc="Method: 0 = FNIRT w/ bending, \
                1 (default) = FNIRT membrane-energy regularization, \
                2 = ANTs/SyN w/, \
                3 = w/o N4Bias",
            position=5, argstr="-reg %d", mandatory=True

        w:
        type = String, default = "10,10,10", usedefault=True, desc="w",
        position=6, argstr="-w %s", mandatory=True

        msk:
        type = String, default = "a,0,0", usedefault=True, desc="msk",
        position=7, argstr="-msk %s", mandatory=True)


    Outputs:

        brain_file:
            type = File, exists=True, desc="extracted brain from atlas_brex"

    """
    input_spec = AtlasBREXInputSpec
    output_spec = AtlasBREXOutputSpec

    _cmd = 'bash'

    def _format_arg(self, name, spec, value):

        import os
        import shutil

        cur_dir = os.getcwd()

        if name == 'script_atlas_BREX':
            shutil.copy(value,cur_dir)
            value = os.path.split(value)[1]

        if name == 'NMT_SS_file':
            shutil.copy(value,cur_dir)
            value = os.path.split(value)[1]

        if name == 'NMT_file':
            shutil.copy(value,cur_dir)
            value = os.path.split(value)[1]

        if name == 't1_restored_file':
            shutil.copy(value,cur_dir)
            value = os.path.split(value)[1]

        return super(AtlasBREX, self)._format_arg(name, spec, value)

    def _list_outputs(self):

        import os
        from nipype.utils.filemanip import split_filename as split_f

        outputs = self._outputs().get()

        path, fname, ext = split_f(self.inputs.t1_restored_file)
        outputs["brain_file"] = os.path.abspath(fname + '_brain' + ext)
        return outputs

#def apply_atlasBREX(t1_restored_file, script_atlas_BREX, NMT_file, NMT_SS_file):
    #"""
    #Wrap of atlasBREX_fslfrioul.sh, the dirty way...
    #"""
    #import os
    #import shutil

    #from nipype.utils.filemanip import split_filename as split_f


    #### all files need to be copied in cur_dir
    #cur_dir = os.getcwd()

    #shutil.copy(NMT_file, cur_dir)
    #shutil.copy(NMT_SS_file, cur_dir)
    #shutil.copy(t1_restored_file, cur_dir)
    #shutil.copy(script_atlas_BREX, cur_dir)

    #path, fname, ext = split_f(t1_restored_file)

    ### just to be sure...
    #os.chdir(cur_dir)

    #if ext == ".nii":
        #print("zipping {} as expected by atlas_brex".format(t1_restored_file))
        #os.system("gzip {}".format(fname+ ext))
        #ext = ".nii.gz"

    #cmd = "bash {} -b {} -nb {} -h {} -f 0.5 -reg 1 -w 10,10,10 -msk a,0,0".format(os.path.split(script_atlas_BREX)[1], os.path.split(NMT_SS_file)[1], os.path.split(NMT_file)[1], fname + ext)
    #print (cmd)
    #os.system(cmd)

    ###get mask filename
    #brain_file=os.path.abspath(fname + "_brain" + ext)

    #return brain_file

#def apply_atlasBREX(t1_restored_file):
    #"""
    #Wrap of atlasBREX_fslfrioul.sh, the dirty way...
    #"""
    #import os
    #import shutil

    #from nipype.utils.filemanip import split_filename as split_f

    #cur_dir = os.path.abspath("")
    #print(cur_dir)

    #script_dir = "/hpc/meca/users/loh.k/macaque_preprocessing/preproc_cloud/processing_scripts/"
    #script_atlas_BREX = os.path.join(script_dir,"atlasBREX_fslfrioul.sh")
    #shutil.copy(script_atlas_BREX,cur_dir)

    #### all files need to be copied in cur_dir
    #nmt_dir="/hpc/meca/users/loh.k/macaque_preprocessing/NMT_v1.2/"
    #nmt_file = os.path.join(nmt_dir,"NMT.nii.gz")
    #shutil.copy(nmt_file,cur_dir)

    #nmt_ss_file = os.path.join(nmt_dir,"NMT_SS.nii.gz")
    #shutil.copy(nmt_ss_file,cur_dir)

    #path, fname, ext = split_f(t1_restored_file)
    #print(path, fname, ext)
    #shutil.copy(t1_restored_file,cur_dir)


    ### just to be sure...
    #os.chdir(cur_dir)

    #if ext == ".nii":
        #print("zipping {} as expected by atlas_brex".format(t1_restored_file))
        #os.system("gzip {}".format(fname+ ext))
        #ext = ".nii.gz"

    #os.system("bash {} -b {} -nb {} -h {} -f 0.5 -reg 1 -w 10,10,10 -msk a,0,0".format("atlasBREX_fslfrioul.sh", "NMT_SS.nii.gz", "NMT.nii.gz", fname + ext))

    ###get mask filename
    #brain_file=os.path.abspath(fname + "_brain" + ext)

    #return brain_file
