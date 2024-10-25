

```yaml
name: FE
workers:
  example_worker:
    type: local
    scheduler_type: slurm
    work_dir: /pscratch/sd/c/cyrusyc/.jfremote
    pre_run: module load python; source activate /pscratch/sd/c/cyrusyc/.conda/comm
    timeout_execute: 60
    # host: perlmutter.nersc.gov
    # user: cyrusyc
  batch_worker:
    type: local
    scheduler_type: slurm
    work_dir: /pscratch/sd/c/cyrusyc/.jfremote
    pre_run: module load python; source activate /pscratch/sd/c/cyrusyc/.conda/comm
    # host: hpc_host
    max_jobs: 100
    batch:
      jobs_handle_dir: /pscratch/sd/c/cyrusyc/.jfremote
      work_dir: /pscratch/sd/c/cyrusyc/.jfremote
      max_wait: 50
queue:
  store:
    type: MongoStore
    host: mongodb05.nersc.gov
    database: db
    username: alex
    password: password
    collection_name: jobs
exec_config: {}
jobstore:
  docs_store:
    type: MongoStore
    database: db
    host: mongodb05.nersc.gov
    port: 27017
    username: alex
    password: password
    collection_name: outputs
  additional_stores:
    data:
      type: GridFSStore
      database: db
      host: mongodb05.nersc.gov
      port: 27017
      username: alex
      password: password
      collection_name: outputs_blobs
```

```bash
export jfremote_project=project_name
```

```bash
jf project check --errors
```
 

```bash
jf admin reset
```
