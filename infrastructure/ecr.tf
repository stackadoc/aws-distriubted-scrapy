resource "aws_ecr_repository" "stackabot_repo" {
  name = "stackabot-repo"
}

resource "docker_image" "stackabot_docker_image" {
  name = "${aws_ecr_repository.stackabot_repo.repository_url}:latest"
  build {
    context = var.dockerfile_path
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset(path.root, "docker/*") : filesha1(f)]))
  }
}

resource "docker_registry_image" "image_handler" {
  name = docker_image.stackabot_docker_image.name
}