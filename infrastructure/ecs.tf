resource "aws_ecs_cluster" "stackabot_cluster" {
  name = "stackabot-cluster"

}

resource "aws_ecs_capacity_provider" "ecs_capacity_provider" {
  name = "stackabot-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn         = aws_autoscaling_group.stackabot_autoscaling_group.arn
    managed_termination_protection = "DISABLED"

    managed_scaling {
      maximum_scaling_step_size = 2
      minimum_scaling_step_size = 1
      status                    = "ENABLED"
      target_capacity           = 100
    }
  }
}

resource "aws_ecs_cluster_capacity_providers" "example" {
  cluster_name = aws_ecs_cluster.stackabot_cluster.name

  capacity_providers = [aws_ecs_capacity_provider.ecs_capacity_provider.name]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = aws_ecs_capacity_provider.ecs_capacity_provider.name
  }
}

resource "aws_cloudwatch_log_group" "client_log_group" {
  name = "/ecs/scrapy-client-logs"
  skip_destroy = true
  retention_in_days = 7
}

resource "aws_ecs_task_definition" "scrapy_task_definition" {
  family             = "scrapy-client"
  network_mode       = "awsvpc"
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  execution_role_arn = aws_iam_role.ecs_exec_role.arn
  cpu                = 4096
  memory             = 15722
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "scrapy-client"
      image     = "${aws_ecr_repository.stackabot_repo.repository_url}:latest"
      cpu       = 4096
      memory    = 15722
      essential = true

      linuxParameters = {
        initProcessEnabled = true
      }
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-create-group  = "true"
          awslogs-group         = "${aws_cloudwatch_log_group.server_log_group.id}"
          awslogs-region        = "eu-west-3"
          awslogs-stream-prefix = "ecs"
        }
      }

    }
  ])

}


resource "aws_ecs_service" "scrapy_service" {
  name                   = "sc-service"
  cluster                = aws_ecs_cluster.stackabot_cluster.id
  task_definition        = aws_ecs_task_definition.scrapy_task_definition.arn
  desired_count          = 0
  enable_execute_command = true

  network_configuration {
    subnets         = aws_subnet.public[*].id
  }

  force_new_deployment = true

  triggers = {
    redeployment = true
  }

  capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.ecs_capacity_provider.name
    weight            = 100
  }

  lifecycle {
    ignore_changes = [desired_count]
  }

}