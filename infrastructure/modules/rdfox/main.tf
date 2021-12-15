// Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


resource "kubernetes_secret" "rdfox-license" {
  metadata {
    name      = "rdfox-license"
    namespace = var.namespace
  }

  data = {
    "RDFox.lic" = base64decode(filebase64("${var.license_path}"))
  }
}

resource "kubernetes_secret" "rdfox-password" {
  metadata {
    name      = "rdfox-password"
    namespace = var.namespace
  }

  data = {
    "password" = base64encode(var.password)
  }
}

resource "kubernetes_ingress" "rdfox" {
  wait_for_load_balancer = true
  metadata {
    namespace = var.namespace
    name      = "rdfox"
    annotations = {
      "kubernetes.io/ingress.class"                = "alb"
      "alb.ingress.kubernetes.io/scheme"           = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"      = "ip"
      "alb.ingress.kubernetes.io/healthcheck-path" = "/health"
      "alb.ingress.kubernetes.io/success-codes"    = "200,204"
      "alb.ingress.kubernetes.io/security-groups"  = var.security_group
      "alb.ingress.kubernetes.io/certificate-arn"  = var.acm_cert
    }
  }
  spec {
    rule {
      http {
        path {
          path = "/*"
          backend {
            service_name = kubernetes_service.rdfox.metadata.0.name
            service_port = var.rdfox_port
          }
        }
      }
    }
  }
}

# Display load balancer hostname (typically present in AWS)
output "alb_hostname" {
  value = kubernetes_ingress.rdfox.status.0.load_balancer.0.ingress.0.hostname
}

# Display load balancer IP (typically present in GCP, or using Nginx ingress controller)
output "alb_ip" {
  value = kubernetes_ingress.rdfox.status.0.load_balancer.0.ingress.0.ip
}

resource "kubernetes_service" "rdfox" {
  metadata {
    name      = "rdfox"
    namespace = var.namespace
  }
  spec {
    selector = {
      app         = "rdfox"
      rdfoxexpose = "aye"
    }
    port {
      port        = var.rdfox_port
      target_port = var.rdfox_port
    }
    #type = "LoadBalancer"
  }
}



resource "kubernetes_deployment" "rdfox_deployment" {
  metadata {
    name = "rdfox-deployment"
    labels = {
      app = "rdfox"
    }
    namespace = var.namespace
  }

  spec {
    replicas = var.persistent_replicas

    selector {
      match_labels = {
        app = "rdfox"
      }
    }

    template {
      metadata {
        labels = {
          app = "rdfox"
        }
        namespace = var.namespace
      }

      spec {

        service_account_name = var.rdfox_service_account
        security_context {
          fs_group = 1337
        }
        container {
          image = "oxfordsemantic/rdfox"
          name  = "rdfox"
          args  = ["-persist-roles", "off", "-persist-ds", "off", "daemon"]
          env {
            name  = "RDFOX_ROLE"
            value = "SUPER"
          }

          env {
            name  = "RDFOX_PASSWORD"
            value = "SECRET"
          }

          port {
            container_port = var.rdfox_port
          }

          resources {
            limits = {
              cpu    = "80"
              memory = "32Gi"
            }
            requests = {
              cpu    = "250m"
              memory = "50Mi"
            }
          }


          volume_mount {
            name       = "license"
            mount_path = "/home/rdfox/.RDFox"
            read_only  = true
          }


          liveness_probe {
            http_get {
              path = "/health"
              port = var.rdfox_port
            }
            initial_delay_seconds = 3
            period_seconds        = 3
          }
        }
        volume {
          name = "license"
          secret {
            secret_name = "rdfox-license"
          }
        }


      }
    }
  }
}
