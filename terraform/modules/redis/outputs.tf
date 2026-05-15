output "id" {
  description = "The ID of the Redis instance"
  value       = google_redis_instance.cache.id
}

output "host" {
  description = "The IP address of the instance"
  value       = google_redis_instance.cache.host
}

output "port" {
  description = "The port number of the instance"
  value       = google_redis_instance.cache.port
}
