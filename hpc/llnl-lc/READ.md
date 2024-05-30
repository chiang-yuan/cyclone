

## Account
```bash
sacctmgr show user <username>
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