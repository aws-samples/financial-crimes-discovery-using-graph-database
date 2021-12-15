## HOWTO
Use the information and scripts to schedule performance tests. See job_submitter for a script that generates and upload job specs thus triggering jobs

## Useful commands for tshoot/debug

`kubectl get pods --namespace ns-rdfox --watch # See status of all pods/jobs good to monitor when submitting a job so you see if it's triggering`
`watch -d kubectl exec JOBNAME  -- df -h # will show you disk usage`
`kubectl exec -it datageneratorsd2nv-fjp4r --container-name the_name -- /bin/bash # gets you a shell into your pod/container`
`kubectl logs --follow datageneratorsd2nv-fjp4r --container-name the_name # tail the container logs`

## Notes
* If the container runs out of memory it will get OOMkilled
* Adding more memory than needed won't further improve performance