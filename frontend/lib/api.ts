import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface TaskStatus {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  current_page: number;
  total_pages: number;
  output_file: string | null;
  error: string | null;
}

export interface UploadResponse {
  task_id: string;
  filename: string;
  status: string;
  message: string;
}

export const uploadPdf = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<UploadResponse>(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getTaskStatus = async (taskId: string): Promise<TaskStatus> => {
  const response = await axios.get<TaskStatus>(`${API_BASE_URL}/status/${taskId}`);
  return response.data;
};

export const downloadMarkdown = async (taskId: string, filename: string) => {
  const response = await axios.get(`${API_BASE_URL}/download/${taskId}`, {
    responseType: 'blob',
  });

  // Create a link to download the file
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${filename.replace('.pdf', '')}.md`);
  document.body.appendChild(link);
  link.click();
  link.parentNode?.removeChild(link);
};

export const getMarkdownContent = async (taskId: string): Promise<string> => {
  const response = await axios.get(`${API_BASE_URL}/download/${taskId}`, {
    responseType: 'text',
  });
  return response.data;
};
