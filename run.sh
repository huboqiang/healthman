source /cluster/home/bqhu_jh/share/miniconda3/etc/profile.d/conda.sh
conda activate cuda1.7

# step1
# Rscript 00.read_rds_files.R

# step2
conda activate bigdata
jupyter nbconvert --execute --inplace --to notebook 0.generate_tableOnePlus.ipynb

# step3, 7 tasks paralell
 conda activate cuda1.7
ls Table1.ipynb Figure*ipynb | xargs -I {} -P 7 bash -c "jupyter nbconvert --execute --inplace --to notebook {}"
