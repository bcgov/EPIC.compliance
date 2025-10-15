import { StaffUser } from "./Staff";

export interface RequirementImage {
  id?: number;
  dbId?: number;
  requirement_id?: number;
  caption?: string;
  taken_by_id?: number;
  taken_by?: StaffUser;
  sort_order?: number;
  image_type?: string;
  original_file_name?: string;
  date_taken?: string;
  relative_url?: string;
  url?: string;
  is_active?: boolean;
}

export interface RequirementImages {
  photos: RequirementImage[];
  figures: RequirementImage[];
}

export interface ImageAPIData {
  id?: number;
  original_file_name?: string;
  date_taken?: string;
  taken_by_id?: number;
  caption?: string;
  relative_url?: string;
}
export interface ImageFormData {
  file?: File;
  fileUrl?: string;
  caption?: string;
  takenBy?: StaffUser;
}

export interface ImageUploadAPIData {
  inspectionId: number;
  fileName: string;
  file: File;
}
export interface PresignedUrlRequestPayload {
  relative_url: string;
  action?: string;
}

export interface UploadedImageFile {
  presigned_url: string;
  relative_url: string;
  fileName: string;
}
