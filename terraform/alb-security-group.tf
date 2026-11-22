resource "aws_security_group" "alb" {
  name_prefix = "shopsphere-phase9-alb-"
  description = "Public HTTPS access for ShopSphere EKS ALB"
  vpc_id      = "vpc-013bd46519b077750"

  tags = {
    Name = "shopsphere-phase9-alb-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTPS from internet"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTP for HTTPS redirect"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_outbound" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow outbound traffic to EKS targets"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
