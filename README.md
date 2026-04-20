# APAC Visualizer++
![MOL?LU](assets/mollu.webp)

Visualizer for dealer and plant overview

See [kimiroo/apac-visualizer-admin](https://github.com/kimiroo/apac-visualizer-admin) for Admin Console image

Sample docker-compose.yaml file
```yaml
services:
    apac-visualizer:
        image: ghcr.io/kimiroo/apac-visualizer:latest
        container_name: apac-visualizer
        ports:
            - "8501:8501"
        volumes:
            - "apac_visualizer_data:/data:ro"
        depends_on:
            apac-visualizer-admin:
                condition: service_healthy
    apac-visualizer-admin:
        image: ghcr.io/kimiroo/apac-visualizer-admin:latest
        container_name: apac-visualizer-admin
        ports:
            - "8502:8501"
        volumes:
            - "apac_visualizer_data:/data"
volumes:
    apac_visualizer_data:
```