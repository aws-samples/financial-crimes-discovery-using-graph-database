# Helper scripts

## delete_database 

This is extremely dangerous and perform a neptune DB reset as per https://aws.amazon.com/blogs/database/resetting-your-graph-data-in-amazon-neptune-in-seconds/ proceed with caution. This primarily exists to perform performance testing without having duplicates (from previous loads)

```source dev.env```
```poetry python delete_database.py```

## bulk_load_data 

```source dev.env```
```poetry python bulk_load_data.py```
