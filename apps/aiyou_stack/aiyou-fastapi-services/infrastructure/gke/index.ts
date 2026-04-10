/**
 * PNKLN Core Stack™ - GKE Infrastructure
 * Pulumi TypeScript Infrastructure as Code
 *
 * Deploys:
 * - GKE Standard cluster with GPU node pools
 * - GKE Autopilot cluster for stateless services
 * - Storage: GCS, Filestore, Cloud SQL, Memorystore
 * - Security: Workload Identity, Binary Authorization, Cloud Armor
 * - Networking: VPC, Load Balancer, Cloud CDN
 */

import * as pulumi from "@pulumi/pulumi";
import * as gcp from "@pulumi/gcp";
import * as k8s from "@pulumi/kubernetes";

// Configuration
const config = new pulumi.Config();
const projectId = config.require("gcp:project");
const region = config.get("region") || "us-central1";
const clusterName = config.get("clusterName") || "pnkln-main";

// ============================================================================
// VPC Network
// ============================================================================

const network = new gcp.compute.Network("pnkln-vpc", {
  autoCreateSubnetworks: false,
  description: "PNKLN Core Stack VPC",
});

const subnet = new gcp.compute.Subnetwork("gke-subnet", {
  network: network.id,
  region: region,
  ipCidrRange: "10.0.0.0/24",
  secondaryIpRanges: [
    {
      rangeName: "pods",
      ipCidrRange: "10.4.0.0/14", // 262k pods
    },
    {
      rangeName: "services",
      ipCidrRange: "10.8.0.0/20", // 4k services
    },
  ],
  privateIpGoogleAccess: true,
});

// ============================================================================
// GKE Standard Cluster (GPU Workloads)
// ============================================================================

const standardCluster = new gcp.container.Cluster("pnkln-standard", {
  name: clusterName,
  location: region,

  // Networking
  network: network.name,
  subnetwork: subnet.name,
  ipAllocationPolicy: {
    clusterSecondaryRangeName: "pods",
    servicesSecondaryRangeName: "services",
  },

  // Private cluster configuration
  privateClusterConfig: {
    enablePrivateNodes: true,
    enablePrivateEndpoint: false, // Keep master accessible for CI/CD
    masterIpv4CidrBlock: "10.100.0.0/28",
  },

  // Master authorized networks (restrict API access)
  masterAuthorizedNetworksConfig: {
    cidrBlocks: [
      {
        cidrBlock: "0.0.0.0/0", // TODO: Restrict to GitHub Actions IPs in production
        displayName: "All (development only)",
      },
    ],
  },

  // Release channel for automatic updates
  releaseChannel: {
    channel: "REGULAR",
  },

  // Workload Identity
  workloadIdentityConfig: {
    workloadPool: `${projectId}.svc.id.goog`,
  },

  // Binary Authorization
  binaryAuthorization: {
    evaluationMode: "PROJECT_SINGLETON_POLICY_ENFORCE",
  },

  // Addons
  addonsConfig: {
    gcePersistentDiskCsiDriverConfig: {
      enabled: true,
    },
    gkeBackupAgentConfig: {
      enabled: true,
    },
    networkPolicyConfig: {
      disabled: false,
    },
  },

  // Node pool configuration (default pool - will be minimal)
  initialNodeCount: 1,
  removeDefaultNodePool: true,

  // Logging and monitoring
  loggingService: "logging.googleapis.com/kubernetes",
  monitoringService: "monitoring.googleapis.com/kubernetes",

  // Shielded nodes
  nodeConfig: {
    shieldedInstanceConfig: {
      enableSecureBoot: true,
      enableIntegrityMonitoring: true,
    },
  },
});

// ============================================================================
// GPU Node Pool (NVIDIA H100)
// ============================================================================

const nvidiaH100Pool = new gcp.container.NodePool("nvidia-h100-pool", {
  cluster: standardCluster.name,
  location: standardCluster.location,

  nodeCount: 2,
  autoscaling: {
    minNodeCount: 2,
    maxNodeCount: 16,
  },

  nodeConfig: {
    machineType: "a3-highgpu-8g",

    // GPU configuration
    guestAccelerators: [
      {
        type: "nvidia-h100-80gb",
        count: 8,
        gpuDriverInstallationConfig: {
          gpuDriverVersion: "LATEST",
        },
      },
    ],

    // Spot VMs for cost optimization (60% savings)
    spot: true,

    // Workload Identity
    workloadMetadataConfig: {
      mode: "GKE_METADATA",
    },

    // OAuth scopes
    oauthScopes: ["https://www.googleapis.com/auth/cloud-platform"],

    // Shielded nodes
    shieldedInstanceConfig: {
      enableSecureBoot: true,
      enableIntegrityMonitoring: true,
    },

    // Metadata
    metadata: {
      "disable-legacy-endpoints": "true",
    },

    // Labels
    labels: {
      "gpu-type": "h100",
      workload: "ml-training",
      "cost-optimization": "spot",
    },

    // Taints (GPU nodes only for GPU workloads)
    taints: [
      {
        key: "nvidia.com/gpu",
        value: "present",
        effect: "NO_SCHEDULE",
      },
    ],
  },

  management: {
    autoRepair: true,
    autoUpgrade: true,
  },
});

// AMD MI300X Node Pool (Month 9+)
const amdMi300xPool = new gcp.container.NodePool(
  "amd-mi300x-pool",
  {
    cluster: standardCluster.name,
    location: standardCluster.location,

    nodeCount: 0, // Start with 0, scale up in month 9
    autoscaling: {
      minNodeCount: 0,
      maxNodeCount: 8,
    },

    nodeConfig: {
      machineType: "a3-mega-8g-amd", // Placeholder - verify actual machine type

      workloadMetadataConfig: {
        mode: "GKE_METADATA",
      },

      oauthScopes: ["https://www.googleapis.com/auth/cloud-platform"],

      labels: {
        "gpu-type": "mi300x",
        workload: "ml-training",
        diversification: "amd",
      },

      taints: [
        {
          key: "amd.com/gpu",
          value: "present",
          effect: "NO_SCHEDULE",
        },
      ],
    },

    management: {
      autoRepair: true,
      autoUpgrade: true,
    },
  },
  { dependsOn: [standardCluster] },
);

// ============================================================================
// GKE Autopilot Cluster (Stateless Services)
// ============================================================================

const autopilotCluster = new gcp.container.Cluster("pnkln-autopilot", {
  name: "pnkln-autopilot",
  location: region,

  // Enable Autopilot
  enableAutopilot: true,

  // Networking
  network: network.name,
  subnetwork: subnet.name,
  ipAllocationPolicy: {
    clusterSecondaryRangeName: "pods",
    servicesSecondaryRangeName: "services",
  },

  // Release channel
  releaseChannel: {
    channel: "REGULAR",
  },

  // Workload Identity
  workloadIdentityConfig: {
    workloadPool: `${projectId}.svc.id.goog`,
  },

  // Binary Authorization
  binaryAuthorization: {
    evaluationMode: "PROJECT_SINGLETON_POLICY_ENFORCE",
  },
});

// ============================================================================
// Storage Layer
// ============================================================================

// GCS Buckets
const videoBucket = new gcp.storage.Bucket("pnkln-video-prod", {
  name: `${projectId}-video-prod`,
  location: region,
  storageClass: "STANDARD",

  uniformBucketLevelAccess: true,

  lifecycleRules: [
    {
      action: { type: "SetStorageClass", storageClass: "NEARLINE" },
      condition: { age: 90 },
    },
    {
      action: { type: "SetStorageClass", storageClass: "COLDLINE" },
      condition: { age: 365 },
    },
  ],

  versioning: {
    enabled: true,
  },
});

const modelBucket = new gcp.storage.Bucket("pnkln-models", {
  name: `${projectId}-models`,
  location: region,
  storageClass: "STANDARD",

  uniformBucketLevelAccess: true,

  versioning: {
    enabled: true,
  },
});

// Filestore (NFS for ML workspace)
const filestore = new gcp.filestore.Instance("ml-workspace", {
  name: "ml-workspace",
  location: `${region}-a`, // Zonal
  tier: "ENTERPRISE", // High throughput for GPU workloads

  fileShares: {
    capacityGb: 10240, // 10TB
    name: "ml_data",
  },

  networks: [
    {
      network: network.name,
      modes: ["MODE_IPV4"],
    },
  ],
});

// Cloud SQL (PostgreSQL)
const dbInstance = new gcp.sql.DatabaseInstance("pnkln-db", {
  name: "pnkln-db",
  region: region,
  databaseVersion: "POSTGRES_15",

  settings: {
    tier: "db-custom-8-32768", // 8 vCPU, 32GB RAM

    availabilityType: "REGIONAL", // HA

    backupConfiguration: {
      enabled: true,
      pointInTimeRecoveryEnabled: true,
      backupRetentionSettings: {
        retainedBackups: 30,
      },
    },

    ipConfiguration: {
      ipv4Enabled: false, // Private IP only
      privateNetwork: network.id,
    },

    databaseFlags: [
      {
        name: "max_connections",
        value: "1000",
      },
    ],
  },

  deletionProtection: true,
});

// Memorystore (Redis)
const redisInstance = new gcp.redis.Instance("pnkln-cache", {
  name: "pnkln-cache",
  region: region,
  tier: "STANDARD_HA",
  memorySizeGb: 5,

  redisVersion: "REDIS_7_0",

  authorizedNetwork: network.id,

  redisConfigs: {
    "maxmemory-policy": "allkeys-lru",
  },
});

// ============================================================================
// Security: Binary Authorization
// ============================================================================

const coverageAttestor = new gcp.binaryauthorization.Attestor("coverage-98-attestor", {
  name: "coverage-98-attestor",
  attestationAuthorityNote: {
    noteReference: pulumi.interpolate`projects/${projectId}/notes/coverage-98-note`,
  },
});

const securityAttestor = new gcp.binaryauthorization.Attestor("security-scan-attestor", {
  name: "security-scan-attestor",
  attestationAuthorityNote: {
    noteReference: pulumi.interpolate`projects/${projectId}/notes/security-scan-note`,
  },
});

// ============================================================================
// Kubernetes Provider
// ============================================================================

const k8sProvider = new k8s.Provider("gke-k8s", {
  kubeconfig: standardCluster.name.apply(async (name) => {
    const creds = await gcp.container.getCluster({
      name: name,
      location: region,
    });

    const clusterEndpoint = creds.endpoint;
    const clusterCaCert = creds.masterAuth.clusterCaCertificate;

    return pulumi.interpolate`apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: ${clusterCaCert}
    server: https://${clusterEndpoint}
  name: ${name}
contexts:
- context:
    cluster: ${name}
    user: ${name}
  name: ${name}
current-context: ${name}
kind: Config
users:
- name: ${name}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl
      provideClusterInfo: true`;
  }),
});

// ============================================================================
// Exports
// ============================================================================

export const standardClusterName = standardCluster.name;
export const standardClusterEndpoint = standardCluster.endpoint;
export const autopilotClusterName = autopilotCluster.name;
export const autopilotClusterEndpoint = autopilotCluster.endpoint;

export const videoBucketName = videoBucket.name;
export const modelBucketName = modelBucket.name;
export const filestoreIp = filestore.networks[0].ipAddresses[0];
export const dbConnectionName = dbInstance.connectionName;
export const redisHost = redisInstance.host;
export const redisPort = redisInstance.port;

export const networkName = network.name;
export const subnetName = subnet.name;
