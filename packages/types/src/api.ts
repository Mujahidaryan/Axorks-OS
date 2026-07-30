export interface ApiResponse<T = any> {
  data: T | null;
  meta: {
    page?: number;
    per_page?: number;
    total?: number;
    total_pages?: number;
    [key: string]: any;
  } | null;
  errors: Array<{ message: string; field?: string }> | null;
}
