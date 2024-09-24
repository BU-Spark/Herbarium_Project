# Build and Run Instructions
## **Build the Docker Image:**  
   Navigate to the directory containing the Dockerfile and run:
   ```sh
   docker build --build-arg CONDA_ENV_NAME=<your-conda-env-name> -t my-herbarium-app .
   ```
   Replace `<your-conda-env-name>` with the desired conda environment name.

> ### Notes
> - If you don't provide the `--build-arg` while building, the default value `trocr_env` will be used as the conda environment name.
> - Remember to replace `<your-conda-env-name>` with the actual name you want to give to your conda environment when building the Docker image.

## **Run the Docker Container:**  
### Using Docker Bind Mounts
When you run your Docker container, you can use the `-v` or `--mount` flag to bind-mount a directory or a file from your host into your container.

#### Example
If you have the input images in a directory named `images` on your host, you can mount this directory to a directory inside your container like this:
```sh
docker run -v $(pwd)/images:/usr/src/app/images -p 8888:8888 my-herbarium-app
```
or
```sh
docker run --mount type=bind,source=$(pwd)/images,target=/usr/src/app/images -p 8888:8888 my-herbarium-app
```

Here:
- `$(pwd)/images` is the absolute path to the `images` directory on your host machine.
- `/usr/src/app/images` is the path where the `images` directory will be accessible from within your container.

> ### Note
> When using bind mounts, any changes made to the files in the mounted directory will be reflected in both the host and the container, since they are actually the same files on the host’s filesystem.

> ### Modification in Script
> We would need to modify the script to read images from the mounted directory (`/usr/src/app/images` in this example) instead of the original host directory.
