# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


FROM oxfordsemantic/rdfox
USER root
RUN apt-get update
WORKDIR /
COPY start.sh start.sh
RUN chmod +x start.sh
RUN id -u rdfox
RUN id -G rdfox
USER rdfox
ENTRYPOINT [ "/bin/bash", "-c" ]
CMD [ "./start.sh"]