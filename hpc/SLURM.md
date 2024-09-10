

- Cancel job with certain job name pattern
```bash
squeue --me -o "%.18i %.50j" | awk '/stability-/{print $1}' | xargs scancel
```


- Cancel job in a certain node and after a certain job id
```bash
squeue --me -p regular_milan_ss11 -h -o "%i" | awk '$1 > 30316092' | xargs scancel
```


- Check the running jobs
```bash
squeue --me -t R
```
