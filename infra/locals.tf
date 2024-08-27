locals {
  datasetsArray = jsondecode(file("${path.module}/datasets.json"))
  datasetsMap   = { for idx, val in local.datasetsArray : idx => val }
}
