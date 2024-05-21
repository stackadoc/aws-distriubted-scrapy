resource "aws_ecr_repository" "distributed_scraping_repository" {
  name = "distributed-craping-repository"
}

resource "docker_image" "distributed_scraping_docker_image" {
  name = "${aws_ecr_repository.distributed_scraping_repository.repository_url}:latest"
  build {
    context = "${path.root}/../docker/*"
  }
  triggers = {
    dir_sha1 = sha1(join("", [for f in fileset("${path.root}/..", "docker/*") : filesha1(f)]))
  }
}

resource "docker_registry_image" "image_handler" {
  name = docker_image.distributed_scraping_docker_image.name
}