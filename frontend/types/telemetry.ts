// GET /api/dev/stats/: inventory and anonymous estimates, never provider invoices.
export type DevStats = {
  generated_at: string;
  period: { from: string; to: string; timezone: string };
  maps: {
    measurement: string;
    total: number;
    daily: { day: string; screen: string; provider: string; loads: number }[];
    billing_equivalent: boolean;
    limitations: string;
  };
  images: {
    registered_files: number;
    cloudinary_references: number;
    local_references: number;
    storage_bytes: number | null;
    bandwidth_bytes: number | null;
    transformations: number | null;
  };
  documents: {
    registered_versions: number;
    current_versions: number;
    registered_bytes_all_versions: number;
    storage: string;
  };
  unmeasured: string[];
  inventory_note: string;
};
