

## Account
```bash
sacctmgr show user <username>
```

## Virutla Environment

```bash
virtualenv --system-site-packages /usr/workspace/$USER/.local/$SYS_TYPE/<venv name>
```

## Job

**Debug**
```bash
srun -p pdebug -N <nnodes> -n <ntasks> <exe>
```

**Batch**
```bash
srun -p pbatch -N <nnodes> -n <ntasks> <exe>
```

**Interative**
```bash
salloc -N <nnodes> -ppsummer -t <time>
```