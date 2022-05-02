
# 2kzw_patch_1e-3r_lenx_NM_10p_2000k_1f
# with include_lenx
rm all_script.txt
rm get_result.sh
for m in patch slice
do
    for r in 1e-3 1 10
    do
        for o in Nelder-Mead L-BFGS-B
        do 
            for p in 10 26
            do
                for k in 500 2000
                do
                    for f in 1
                    do
                        DIR_NAME=2kzw_${m}_${r}r_lenx_${o}_${p}p_${k}k_${f}f
                        mkdir -p $DIR_NAME
                        echo "denss.py -f 2kzw.dat -o $DIR_NAME/result --seed 42 -d 134 -n 64 --reg_scaling --reg_method ${m} --reg_coeff ${r} --opt_method ${o} --num_patch ${p} --reg_kick_in ${k} --reg_kick_freq ${f}" > $DIR_NAME/denss_scan.sh
                        echo "denss.align.py -f $DIR_NAME/result.mrc -ref 2kzw.mrc -o $DIR_NAME/aligned" >> $DIR_NAME/denss_scan.sh
                        echo "denss.calcfsc.py -f $DIR_NAME/aligned.mrc -ref 2kzw.mrc -o $DIR_NAME/fsc > $DIR_NAME/fsc.txt" >> $DIR_NAME/denss_scan.sh
                        echo "sh ./$DIR_NAME/denss_scan.sh" >> all_script.txt
                        echo "echo $DIR_NAME \`cat $DIR_NAME/fsc.txt\`" >> get_result.sh
                    done
                done
            done
        done
    done
done

# without include_lenx
for m in patch slice
do
    for r in 1e-3 1 10
    do
        for o in Nelder-Mead L-BFGS-B
        do 
            for p in 10 26
            do
                for k in 500 2000
                do
                    for f in 1
                    do
                        DIR_NAME=2kzw_${m}_${r}r_nolenx_${o}_${p}p_${k}k_${f}f
                        mkdir -p $DIR_NAME
                        echo "denss.py -f 2kzw.dat -o $DIR_NAME/result --seed 42 -d 134 -n 64 --reg_scaling --reg_method ${m} --reg_coeff ${r} --include_lenx False --opt_method ${o} --num_patch ${p} --reg_kick_in ${k} --reg_kick_freq ${f}" > $DIR_NAME/denss_scan.sh
                        echo "denss.align.py -f $DIR_NAME/result.mrc -ref 2kzw.mrc -o $DIR_NAME/aligned" >> $DIR_NAME/denss_scan.sh
                        echo "denss.calcfsc.py -f $DIR_NAME/aligned.mrc -ref 2kzw.mrc -o $DIR_NAME/fsc > $DIR_NAME/fsc.txt" >> $DIR_NAME/denss_scan.sh
                        echo "sh ./$DIR_NAME/denss_scan.sh" >> all_script.txt
                        echo "echo $DIR_NAME \`cat $DIR_NAME/fsc.txt\`" >> get_result.sh
                    done
                done
            done
        done
    done
done

head -8 all_script.txt > small_script.txt
