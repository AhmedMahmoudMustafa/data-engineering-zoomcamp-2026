variable "credentials" {
  description = "My Credentials"
  default     = "../keys/gcp_key.json"
  #ex: if you have a directory where this file is called keys with your service account json file
  #saved there as gcp_key.json you could use default = "./keys/gcp_key.json"
}


variable "project" {
  description = "Project"
  default     = "capsone-project-492612"
}

variable "region" {
  description = "Region"
  #Update the below to your desired region
  default = "europe-west2"
}

variable "gcs_location" {
  default = "EUROPE-WEST2"
}

variable "bq_location" {
  default = "EU"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  #Update the below to what you want your dataset to be called
  default = "capsone_findata_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  #Update the below to a unique bucket name
  default = "de-capstone-bucket-findata"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}