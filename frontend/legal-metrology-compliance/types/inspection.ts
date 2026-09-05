export type InspectionCreate = {
  inspection_type: string;
  product_name?: string;
  brand_name?: string;
  manufacturer_name?: string;
  source_url?: string;
};

export type InspectionResponse = {
  id: number;
  inspection_number: string;
  officer_id: number;
  inspection_type: string;
  product_name: string | null;
  brand_name: string | null;
  manufacturer_name: string | null;
  source_url: string | null;
  status: string;
  overall_result: string;
  created_at: string;
  updated_at: string;
};
