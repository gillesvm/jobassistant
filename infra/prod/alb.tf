resource "aws_lb" "jobassistant_alb" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.jobassistant_lb_sg.id]
  subnets            = [aws_subnet.public_jobassistant_a.id, aws_subnet.public_jobassistant_b.id]
}

resource "aws_lb_target_group" "jobassistant_tg" {
  name        = "${local.name_prefix}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.jobassistant_vpc.id
  target_type = "ip"
  health_check {
    path     = "/"
    protocol = "HTTP"
    matcher  = "200"
  }
}

resource "aws_lb_listener" "jobassistant_listener" {
  load_balancer_arn = aws_lb.jobassistant_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.jobassistant_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.jobassistant_tg.arn
  }
}
