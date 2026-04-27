output "cloudfront_url" {
  description = "URL pública del sitio"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "ID de la distribución CloudFront"
  value       = aws_cloudfront_distribution.frontend.id
}

output "api_url" {
  description = "URL base de la API"
  value       = aws_api_gateway_stage.api.invoke_url
}

output "s3_bucket" {
  description = "Nombre del bucket S3"
  value       = aws_s3_bucket.frontend.bucket
}

output "dynamodb_table" {
  description = "Nombre de la tabla DynamoDB"
  value       = aws_dynamodb_table.visits.name
}
