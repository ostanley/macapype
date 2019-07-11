
#### equivalent of flirt_average in FSL
def average_align(list_img):

    import os
    import nibabel as nib
    import numpy as np

    from nipype.utils.filemanip import split_filename as split_f
    import nipype.interfaces.fsl as fsl
    print list_img

    if isinstance(list_img, list):

        assert len(list_img) > 0,"Error, list should have at least one file"

        if len(list_img) == 1:
            assert os.path.exists(list_img[0])
            av_img_file = list_img[0]
        else:

            img_0 = nib.load(list_img[0])
            path, fname, ext  = split_f(list_img[0])

            list_data = [img_0.get_data()]
            for i,img in enumerate(list_img[1:]):

                print("running flirt on {}".format(img))
                flirt  =  fsl.FLIRT(dof = 6)
                #flirt.inputs.output_type = "NIFTI_GZ"
                flirt.inputs.in_file = img
                flirt.inputs.reference = list_img[0]
                flirt.inputs.interp = "sinc"
                flirt.inputs.no_search = True
                #flirt.inputs.out_file = os.path.abspath("tmp_" + str(i) + ext)
                out_file = flirt.run().outputs.out_file
                print (out_file)

                data = nib.load(out_file).get_data()
                list_data.append(data)

                #os.remove(out_file)

            avg_data = np.mean(np.array(list_data), axis = 0)
            print (avg_data.shape)

            av_img_file = os.path.abspath("avg_" + fname + ext)
            nib.save(nib.Nifti1Image(avg_data, header = img_0.get_header(), affine = img_0.get_affine()),av_img_file)

    else:
        assert os.path.exists(list_img)
        av_img_file = list_img

    return av_img_file


def wrap_antsAtroposN4(dimension, shft_aff_file, brainmask_file, numberOfClasses, ex_prior):

    import os
    import shutil
    from nipype.utils.filemanip import split_filename as split_f
    _, prior_fname, prior_ext = split_f(ex_prior[-1]) ## last element

    ### copying file locally
    dest = os.path.abspath("")

    for prior_file in ex_prior[2:]:
        print (prior_file)
        shutil.copy(prior_file,dest)

    shutil.copy(shft_aff_file,dest)
    shutil.copy(brainmask_file,dest)

    _, bmask_fname, bmask_ext = split_f(brainmask_file)
    _, shft_aff_fname, shft_aff_ext = split_f(shft_aff_file)

    ### generating template_file
    #TODO should be used by default
    template_file = "tmp_%02d.nii.gz"

    ### generating bash_line
    os.chdir(dest)

    out_pref = "segment_"
    bash_line = "bash antsAtroposN4.sh -d {} -a {} -x {} -c {} -p {} -o {}".format(
        dimension,shft_aff_fname+ shft_aff_ext ,bmask_fname+bmask_ext,numberOfClasses,template_file,out_pref)
    print("bash_line : "+bash_line)

    os.system(bash_line)

    #out_files = [os.path.abspath(out_pref+"Segmentation"+fname+prior_ext) for fname in ["","Posteriors01","Posteriors02","Posteriors03"]]

    seg_file = os.path.abspath(out_pref+"Segmentation"+prior_ext)
    seg_post1_file = os.path.abspath(out_pref+"SegmentationPosteriors01"+prior_ext)
    seg_post2_file = os.path.abspath(out_pref+"SegmentationPosteriors02"+prior_ext)
    seg_post3_file = os.path.abspath(out_pref+"SegmentationPosteriors03"+prior_ext)

    out_files = [seg_file,seg_post1_file,seg_post2_file,seg_post3_file]

    #TODO surely more robust way can be used
    return out_files, seg_file, seg_post1_file, seg_post2_file, seg_post3_file

########### NMT_subject_align

def wrap_NMT_subject_align(T1_file):

    import os
    import shutil
    from nipype.utils.filemanip import split_filename as split_f

    nmt_dir="/hpc/meca/users/loh.k/macaque_preprocessing/NMT_v1.2/"
    nmt_ss_file = os.path.join(nmt_dir,"NMT_SS.nii.gz")
    #shutil.copy(nmt_ss_file,cur_dir)

    script_file = os.path.join(nmt_dir,"NMT_subject_align.csh")

    path, fname, ext = split_f(nmt_ss_file)
    #shutil.copy(T1_file,cur_dir)

    ## just to be sure...
    #os.chdir(nmt_dir)

    os.system("tcsh -x {} {} {}".format(script_file, nmt_ss_file, T1_file))

    shft_aff_file = os.path.abspath(fname + "_shft_aff" + ext )
    warpinv_file = os.path.abspath(fname + "_shft_WARPINV" + ext )

    transfo_file = os.path.abspath(fname + "_composite_linear_to_NMT.1D")
    inv_transfo_file = os.path.abspath(fname + "_composite_linear_to_NMT_inv.1D")


    return shft_aff_file, warpinv_file, transfo_file, inv_transfo_file

########### add Nwarp
def add_Nwarp(list_prior_files):

    out_files = []
    for prior_file in list_prior_files[:3]:

        path, fname, ext = split_f(prior_file)
        #out_files.append(os.path.join(path,fname + "_Nwarp" + ext))
        out_files.append(fname + "_Nwarp" + ext)

    for i in range(1,4):
        out_files.append("tmp_%02d.nii.gz"%i)

    return out_files