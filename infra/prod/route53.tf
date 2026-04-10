resource "aws_route53_record" "jobassistant_alias" {
  zone_id = data.aws_route53_zone.jobassistant.zone_id
  name    = "${local.app_subdomain}.${local.domain}"
  type    = "A"

  alias {
    name                   = aws_lb.jobassistant_alb.dns_name
    zone_id                = aws_lb.jobassistant_alb.zone_id
    evaluate_target_health = false
  }
}