import { useState, useCallback, useRef } from 'react';
import UploadService, { type UploadProgress, type UploadResponse } from '../services/uploadService';
import { SessionType } from '../types/enums';

export interface UploadState {
  isUploading: boolean;
  progress: UploadProgress | null;
  error: string | null;
  success: boolean;
  response: UploadResponse | null;
}

export const useUpload = () => {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: null,
    error: null,
    success: false,
    response: null
  });

  const xhrRef = useRef<XMLHttpRequest | null>(null);

  const uploadFile = useCallback(async (
    file: Blob,
    sessionType: SessionType
  ): Promise<UploadResponse> => {
    // Validar arquivo antes do upload
    const validation = UploadService.validateFile(file);
    if (!validation.valid) {
      const errorResponse: UploadResponse = {
        success: false,
        error: validation.error
      };
      setUploadState({
        isUploading: false,
        progress: null,
        error: validation.error || 'Arquivo inválido',
        success: false,
        response: errorResponse
      });
      return errorResponse;
    }

    // Resetar estado
    setUploadState({
      isUploading: true,
      progress: null,
      error: null,
      success: false,
      response: null
    });

    try {
      const response = await UploadService.uploadRecording(
        file,
        sessionType,
        (progress: UploadProgress) => {
          setUploadState(prev => ({
            ...prev,
            progress
          }));
        }
      );

      setUploadState({
        isUploading: false,
        progress: null,
        error: response.success ? null : response.error || 'Erro no upload',
        success: response.success,
        response
      });

      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido no upload';
      const errorResponse: UploadResponse = {
        success: false,
        error: errorMessage
      };

      setUploadState({
        isUploading: false,
        progress: null,
        error: errorMessage,
        success: false,
        response: errorResponse
      });

      return errorResponse;
    }
  }, []);

  const cancelUpload = useCallback(() => {
    if (xhrRef.current) {
      UploadService.cancelUpload(xhrRef.current);
      xhrRef.current = null;
    }

    setUploadState({
      isUploading: false,
      progress: null,
      error: 'Upload cancelado',
      success: false,
      response: null
    });
  }, []);

  const resetUpload = useCallback(() => {
    setUploadState({
      isUploading: false,
      progress: null,
      error: null,
      success: false,
      response: null
    });
  }, []);

  const checkStatus = useCallback(async (fileId: string): Promise<UploadResponse> => {
    try {
      const response = await UploadService.checkUploadStatus(fileId);
      return response;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao verificar status'
      };
    }
  }, []);

  return {
    uploadState,
    uploadFile,
    cancelUpload,
    resetUpload,
    checkStatus,
    // Propriedades de conveniência
    isUploading: uploadState.isUploading,
    progress: uploadState.progress,
    error: uploadState.error,
    success: uploadState.success,
    response: uploadState.response
  };
};

export default useUpload;