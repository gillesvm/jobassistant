data "aws_route53_zone" "jobassistant" {
  name         = "${local.domain}"
  private_zone = false
}

resource "aws_acm_certificate" "jobassistant_cert" {
  domain_name = "${local.app_subdomain}.${local.domain}"

  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "jobassistant_cert_validation" {
    for_each = {
        for dvo in aws_acm_certificate.jobassistant_cert.domain_validation_options : dvo.domain_name => {
            name = dvo.resource_record_name
            type = dvo.resource_record_type
            value = dvo.resource_record_value
        }
    }
    zone_id = data.aws_route53_zone.jobassistant.zone_id
    name = each.value.name
    type = each.value.type
    ttl = 60
    records = [each.value.value]
}

resource "aws_acm_certificate_validation" "jobassistant_cert_validation" {
    certificate_arn = aws_acm_certificate.jobassistant_cert.arn
    validation_record_fqdns = [for record in aws_route53_record.jobassistant_cert_validation : record.fqdn]
}