interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

interface UploadResponse {
  success: boolean;
  fileId?: string;
  url?: string;
  message?: string;
  error?: string;
}

export class UploadService {
  private static readonly BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';
  private static readonly UPLOAD_ENDPOINT = '/api/recordings/upload';

  /**
   * Faz upload de um arquivo de gravação para o backend
   */
  static async uploadRecording(
    file: Blob,
    sessionType: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      const fileName = `recording_${Date.now()}.webm`;
      
      // Converte o Blob em File para incluir o nome
      const recordingFile = new File([file], fileName, {
        type: file.type || 'video/webm',
        lastModified: Date.now()
      });

      formData.append('recording', recordingFile);
      formData.append('sessionType', sessionType);
      formData.append('timestamp', new Date().toISOString());
      formData.append('duration', Math.round(file.size / 1000).toString()); // Estimativa baseada no tamanho

      const xhr = new XMLHttpRequest();

      // Configurar callback de progresso
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const progress: UploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100)
            };
            onProgress(progress);
          }
        });
      }

      // Configurar callback de conclusão
      xhr.addEventListener('load', () => {
        try {
          if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);
            resolve({
              success: true,
              fileId: response.fileId,
              url: response.url,
              message: response.message || 'Upload realizado com sucesso'
            });
          } else {
            const errorResponse = JSON.parse(xhr.responseText);
            resolve({
              success: false,
              error: errorResponse.error || `Erro HTTP: ${xhr.status}`
            });
          }
        } catch (error) {
          resolve({
            success: false,
            error: 'Erro ao processar resposta do servidor'
          });
        }
      });

      // Configurar callback de erro
      xhr.addEventListener('error', () => {
        resolve({
          success: false,
          error: 'Erro de rede durante o upload'
        });
      });

      // Configurar callback de timeout
      xhr.addEventListener('timeout', () => {
        resolve({
          success: false,
          error: 'Timeout durante o upload'
        });
      });

      // Configurar timeout (5 minutos)
      xhr.timeout = 5 * 60 * 1000;

      // Iniciar o upload
      xhr.open('POST', `${this.BASE_URL}${this.UPLOAD_ENDPOINT}`);
      xhr.send(formData);
    });
  }

  /**
   * Verifica o status de um upload
   */
  static async checkUploadStatus(fileId: string): Promise<UploadResponse> {
    try {
      const response = await fetch(`${this.BASE_URL}/api/recordings/${fileId}/status`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        ...data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  /**
   * Cancela um upload em andamento
   */
  static cancelUpload(xhr: XMLHttpRequest): void {
    if (xhr && xhr.readyState !== XMLHttpRequest.DONE) {
      xhr.abort();
    }
  }

  /**
   * Valida se o arquivo é válido para upload
   */
  static validateFile(file: Blob): { valid: boolean; error?: string } {
    const maxSize = 100 * 1024 * 1024; // 100MB
    const minSize = 1024; // 1KB
    
    if (file.size > maxSize) {
      return {
        valid: false,
        error: 'Arquivo muito grande. Tamanho máximo: 100MB'
      };
    }

    if (file.size < minSize) {
      return {
        valid: false,
        error: 'Arquivo muito pequeno. Tamanho mínimo: 1KB'
      };
    }

    // Verificar tipo MIME
    const validTypes = ['video/webm', 'video/mp4', 'audio/webm', 'audio/wav'];
    if (file.type && !validTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Tipo de arquivo não suportado. Use WebM, MP4, WAV'
      };
    }

    return { valid: true };
  }

  /**
   * Formata o tamanho do arquivo para exibição
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

export default UploadService;
export type { UploadProgress, UploadResponse };