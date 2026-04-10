resource "aws_security_group" "jobassistant_lb_sg" {
  name        = "jobassistant-lb-sg_allow_tls"
  description = "Allow TLS traffic to the load balancer"
  vpc_id      = aws_vpc.jobassistant_vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "jobassistant_lb_sg_ingress_https" {
  security_group_id = aws_security_group.jobassistant_lb_sg.id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow HTTPS traffic to the load balancer"
}

resource "aws_vpc_security_group_ingress_rule" "jobassistant_lb_sg_ingress_http" {
  security_group_id = aws_security_group.jobassistant_lb_sg.id
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow HTTP traffic to the load balancer"
}

resource "aws_vpc_security_group_egress_rule" "jobassistant_lb_sg_egress_all" {
  security_group_id = aws_security_group.jobassistant_lb_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow all outbound traffic"
}

resource "aws_security_group" "jobassistant_ecs_sg" {
  name        = "jobassistant-ecs-sg"
  description = "Allow trafic to the ECS tasks from the load balancer"
  vpc_id      = aws_vpc.jobassistant_vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "jobassistant_ecs_sg_ingress_container_traffic" {
  security_group_id            = aws_security_group.jobassistant_ecs_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 8000
  to_port                      = 8000
  referenced_security_group_id = aws_security_group.jobassistant_lb_sg.id
  description                  = "Allow container traffic from the load balancer"
}

resource "aws_vpc_security_group_egress_rule" "jobassistant_ecs_sg_egress_all" {
  security_group_id = aws_security_group.jobassistant_ecs_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow all outbound traffic"
}
