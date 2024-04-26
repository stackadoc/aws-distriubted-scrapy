data "aws_ssm_parameter" "ecs_node_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}

resource "aws_launch_template" "stackabot_launch_template" {
  name_prefix   = "stackabot-ecs-template"
  image_id      = data.aws_ssm_parameter.ecs_node_ami.value
  instance_type = "t3.xlarge"

  key_name               = "ecs-key-pair"
  vpc_security_group_ids = [aws_security_group.ec2_security_group.id]
  iam_instance_profile {
    arn = aws_iam_instance_profile.ecs_node.arn
  }

  user_data = base64encode(<<-EOF
      #!/bin/bash
      echo ECS_CLUSTER=${aws_ecs_cluster.stackabot_cluster.name} >> /etc/ecs/ecs.config;
    EOF
  )
}

resource "aws_autoscaling_group" "stackabot_autoscaling_group" {
  name_prefix           = "stackabot-auto-sclaing-group"
  vpc_zone_identifier   = aws_subnet.public[*].id
  desired_capacity      = 0
  max_size              = 5
  min_size              = 0
  health_check_type     = "EC2"
  protect_from_scale_in = false

  launch_template {
    id      = aws_launch_template.stackabot_launch_template.id
    version = "$Latest"
  }

  lifecycle {
    ignore_changes = [desired_capacity]
  }

  tag {
    key                 = "Name"
    value               = "stackabot-ecs-cluster"
    propagate_at_launch = true
  }

  tag {
    key                 = "AmazonECSManaged"
    value               = ""
    propagate_at_launch = true
  }
}

