/**
 * MediaPipe Landmarks Visualizer
 * Visualização melhorada dos pontos do corpo com cores e conexões
 */

class LandmarksVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.isActive = false;
        
        // Configurações de visualização
        this.config = {
            pointRadius: 4,
            lineWidth: 2,
            opacity: 0.8,
            animationSpeed: 0.1,
            smoothingFactor: 0.7
        };
        
        // Cache para suavização de movimento
        this.previousLandmarks = null;
        
        // Cores para diferentes partes do corpo
        this.colors = {
            pose: {
                head: '#FF6B6B',
                torso: '#4ECDC4',
                arms: '#45B7D1',
                legs: '#96CEB4',
                hands: '#FFEAA7',
                feet: '#DDA0DD'
            },
            face: '#FF6B6B',
            hands: '#FFEAA7'
        };
        
        // Conexões da pose (MediaPipe Pose)
        this.poseConnections = [
            // Cabeça
            [0, 1], [1, 2], [2, 3], [3, 7],
            [0, 4], [4, 5], [5, 6], [6, 8],
            [9, 10], [11, 12], [11, 13], [13, 15],
            [12, 14], [14, 16],
            
            // Torso
            [11, 12], [11, 23], [12, 24], [23, 24],
            [23, 25], [24, 26], [25, 27], [26, 28],
            
            // Braços
            [11, 13], [13, 15], [15, 15], [15, 17], [15, 19], [15, 21],
            [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
            
            // Pernas
            [23, 25], [25, 27], [27, 29], [29, 31],
            [24, 26], [26, 28], [28, 30], [30, 32]
        ];
        
        // Conexões das mãos (MediaPipe Hands)
        this.handConnections = [
            [0, 1], [1, 2], [2, 3], [3, 4],
            [0, 5], [5, 6], [6, 7], [7, 8],
            [0, 9], [9, 10], [10, 11], [11, 12],
            [0, 13], [13, 14], [14, 15], [15, 16],
            [0, 17], [17, 18], [18, 19], [19, 20]
        ];
        
        this.setupCanvas();
    }
    
    setupCanvas() {
        // Ajustar tamanho do canvas
        const videoFeed = document.getElementById('videoFeed');
        if (!videoFeed) {
            console.error('❌ Elemento videoFeed não encontrado');
            return;
        }
        
        this.canvas.width = videoFeed.offsetWidth;
        this.canvas.height = videoFeed.offsetHeight;
        
        console.log('🎨 Canvas configurado:', {
            width: this.canvas.width,
            height: this.canvas.height,
            videoFeedWidth: videoFeed.offsetWidth,
            videoFeedHeight: videoFeed.offsetHeight
        });
    }
    
    start() {
        console.log('🚀 LandmarksVisualizer iniciado');
        this.isActive = true;
        this.clear();
    }
    
    stop() {
        this.isActive = false;
        this.clear();
    }
    
    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    // Desenhar um ponto com efeito de brilho e animação
    drawPoint(x, y, color, radius = null) {
        const r = radius || this.config.pointRadius;
        
        // Verificar se as coordenadas são válidas
        if (isNaN(x) || isNaN(y)) {
            console.warn('⚠️ Coordenadas inválidas:', { x, y });
            return;
        }
        
        // Verificar se o ponto está dentro do canvas
        if (x < 0 || x > this.canvas.width || y < 0 || y > this.canvas.height) {
            console.warn('⚠️ Ponto fora do canvas:', { x, y, canvasWidth: this.canvas.width, canvasHeight: this.canvas.height });
            return;
        }
        
        // Efeito de brilho externo
        const outerGradient = this.ctx.createRadialGradient(x, y, 0, x, y, r * 3);
        outerGradient.addColorStop(0, color + '40');
        outerGradient.addColorStop(0.5, color + '20');
        outerGradient.addColorStop(1, 'transparent');
        
        this.ctx.fillStyle = outerGradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y, r * 3, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Efeito de brilho interno
        const innerGradient = this.ctx.createRadialGradient(x, y, 0, x, y, r * 1.5);
        innerGradient.addColorStop(0, color);
        innerGradient.addColorStop(0.7, color + 'CC');
        innerGradient.addColorStop(1, color + '80');
        
        this.ctx.fillStyle = innerGradient;
        this.ctx.beginPath();
        this.ctx.arc(x, y, r * 1.5, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Ponto central sólido
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(x, y, r, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Sombra sutil
        this.ctx.shadowColor = 'rgba(0,0,0,0.3)';
        this.ctx.shadowBlur = 2;
        this.ctx.shadowOffsetX = 1;
        this.ctx.shadowOffsetY = 1;
        this.ctx.fill();
        this.ctx.shadowColor = 'transparent';
    }
    
    // Desenhar uma linha com gradiente e efeitos
    drawLine(x1, y1, x2, y2, color, width = null) {
        const w = width || this.config.lineWidth;
        
        // Sombra da linha
        this.ctx.shadowColor = 'rgba(0,0,0,0.2)';
        this.ctx.shadowBlur = 3;
        this.ctx.shadowOffsetX = 1;
        this.ctx.shadowOffsetY = 1;
        
        // Linha de sombra
        this.ctx.strokeStyle = 'rgba(0,0,0,0.1)';
        this.ctx.lineWidth = w + 2;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
        
        // Resetar sombra
        this.ctx.shadowColor = 'transparent';
        
        // Gradiente na linha principal
        const gradient = this.ctx.createLinearGradient(x1, y1, x2, y2);
        gradient.addColorStop(0, color);
        gradient.addColorStop(0.3, color + 'FF');
        gradient.addColorStop(0.7, color + 'CC');
        gradient.addColorStop(1, color + '80');
        
        this.ctx.strokeStyle = gradient;
        this.ctx.lineWidth = w;
        this.ctx.lineCap = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
        
        // Efeito de brilho na linha
        this.ctx.strokeStyle = color + '40';
        this.ctx.lineWidth = w + 1;
        this.ctx.beginPath();
        this.ctx.moveTo(x1, y1);
        this.ctx.lineTo(x2, y2);
        this.ctx.stroke();
    }
    
    // Converter coordenadas normalizadas para pixels
    normalizeToPixel(x, y) {
        const pixelX = x * this.canvas.width;
        const pixelY = y * this.canvas.height;
        
        // Verificar se a conversão resultou em valores válidos
        if (isNaN(pixelX) || isNaN(pixelY)) {
            console.warn('⚠️ Conversão inválida:', { x, y, pixelX, pixelY, canvasWidth: this.canvas.width, canvasHeight: this.canvas.height });
            return { x: 0, y: 0 };
        }
        
        return {
            x: pixelX,
            y: pixelY
        };
    }
    
    // Suavizar movimento dos landmarks
    smoothLandmarks(landmarks) {
        if (!this.previousLandmarks) {
            this.previousLandmarks = landmarks;
            return landmarks;
        }
        
        const smoothed = [];
        for (let i = 0; i < landmarks.length; i++) {
            if (landmarks[i] && this.previousLandmarks[i]) {
                smoothed.push({
                    x: this.previousLandmarks[i].x * this.config.smoothingFactor + 
                        landmarks[i].x * (1 - this.config.smoothingFactor),
                    y: this.previousLandmarks[i].y * this.config.smoothingFactor + 
                        landmarks[i].y * (1 - this.config.smoothingFactor),
                    z: landmarks[i].z
                });
            } else {
                smoothed.push(landmarks[i]);
            }
        }
        
        this.previousLandmarks = smoothed;
        return smoothed;
    }
    
    // Desenhar landmarks da pose
    drawPoseLandmarks(landmarks) {
        if (!landmarks || !this.isActive) {
            console.log('⚠️ drawPoseLandmarks: dados inválidos ou visualizador inativo');
            return;
        }
        
        console.log('🦴 drawPoseLandmarks:', {
            landmarksCount: landmarks.length,
            firstLandmark: landmarks[0],
            isActive: this.isActive
        });
        
        // Suavizar movimento
        const smoothedLandmarks = this.smoothLandmarks(landmarks);
        
        // Desenhar conexões primeiro
        let connectionsDrawn = 0;
        for (const [start, end] of this.poseConnections) {
            if (smoothedLandmarks[start] && smoothedLandmarks[end]) {
                const startPos = this.normalizeToPixel(smoothedLandmarks[start].x, smoothedLandmarks[start].y);
                const endPos = this.normalizeToPixel(smoothedLandmarks[end].x, smoothedLandmarks[end].y);
                
                // Determinar cor baseada na região
                let color = this.colors.pose.torso;
                if (start <= 16) color = this.colors.pose.head;
                else if (start <= 22) color = this.colors.pose.arms;
                else if (start <= 32) color = this.colors.pose.legs;
                
                this.drawLine(startPos.x, startPos.y, endPos.x, endPos.y, color);
                connectionsDrawn++;
            }
        }
        
        // Desenhar pontos
        let pointsDrawn = 0;
        for (let i = 0; i < smoothedLandmarks.length; i++) {
            const landmark = smoothedLandmarks[i];
            const pos = this.normalizeToPixel(landmark.x, landmark.y);
            
            // Determinar cor baseada no índice
            let color = this.colors.pose.torso;
            if (i <= 16) color = this.colors.pose.head;
            else if (i <= 22) color = this.colors.pose.arms;
            else if (i <= 32) color = this.colors.pose.legs;
            
            this.drawPoint(pos.x, pos.y, color);
            pointsDrawn++;
        }
        
        console.log('✅ Pose desenhada:', { connectionsDrawn, pointsDrawn });
    }
    
    // Desenhar landmarks das mãos
    drawHandLandmarks(hands) {
        if (!hands || !this.isActive) return;
        
        for (const hand of hands) {
            // Desenhar conexões
            for (const [start, end] of this.handConnections) {
                if (hand[start] && hand[end]) {
                    const startPos = this.normalizeToPixel(hand[start].x, hand[start].y);
                    const endPos = this.normalizeToPixel(hand[end].x, hand[end].y);
                    
                    this.drawLine(startPos.x, startPos.y, endPos.x, endPos.y, this.colors.hands);
                }
            }
            
            // Desenhar pontos
            for (const landmark of hand) {
                const pos = this.normalizeToPixel(landmark.x, landmark.y);
                this.drawPoint(pos.x, pos.y, this.colors.hands, 3);
            }
        }
    }
    
    // Desenhar landmarks do rosto
    drawFaceLandmarks(landmarks) {
        if (!landmarks || !this.isActive) return;
        
        // Desenhar pontos principais do rosto
        const keyPoints = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; // Pontos principais
        
        for (const i of keyPoints) {
            if (landmarks[i]) {
                const pos = this.normalizeToPixel(landmarks[i].x, landmarks[i].y);
                this.drawPoint(pos.x, pos.y, this.colors.face, 2);
            }
        }
    }
    
    // Método principal para desenhar todos os landmarks
    drawLandmarks(landmarksData) {
        console.log('🎨 drawLandmarks chamado:', {
            isActive: this.isActive,
            hasPose: !!landmarksData.pose,
            hasHands: !!(landmarksData.hands && landmarksData.hands.length > 0),
            hasFace: !!landmarksData.face
        });
        
        if (!this.isActive) {
            console.log('⚠️ Visualizador não está ativo');
            return;
        }
        
        this.clear();
        
        // Desenhar pose
        if (landmarksData.pose) {
            console.log('🦴 Desenhando pose com', landmarksData.pose.length, 'landmarks');
            this.drawPoseLandmarks(landmarksData.pose);
        }
        
        // Desenhar mãos
        if (landmarksData.hands && landmarksData.hands.length > 0) {
            console.log('✋ Desenhando', landmarksData.hands.length, 'mão(s)');
            this.drawHandLandmarks(landmarksData.hands);
        }
        
        // Desenhar rosto
        if (landmarksData.face) {
            console.log('😊 Desenhando rosto com', landmarksData.face.length, 'landmarks');
            this.drawFaceLandmarks(landmarksData.face);
        }
    }
    
    // Atualizar configurações
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
    
    // Redimensionar canvas
    resize() {
        this.setupCanvas();
    }
    
    // Função de teste para verificar se o visualizador está funcionando
    testVisualization() {
        console.log('🧪 Testando visualização...');
        
        if (!this.isActive) {
            this.start();
        }
        
        // Dados de teste
        const testData = {
            pose: [
                { x: 0.5, y: 0.2, z: 0.0 }, // Cabeça
                { x: 0.5, y: 0.3, z: 0.0 }, // Pescoço
                { x: 0.5, y: 0.5, z: 0.0 }, // Torso
                { x: 0.4, y: 0.6, z: 0.0 }, // Braço esquerdo
                { x: 0.6, y: 0.6, z: 0.0 }, // Braço direito
                { x: 0.5, y: 0.8, z: 0.0 }, // Perna esquerda
                { x: 0.5, y: 0.8, z: 0.0 }  // Perna direita
            ],
            hands: [],
            face: []
        };
        
        this.drawLandmarks(testData);
        console.log('✅ Teste de visualização concluído');
    }
}

// Exportar para uso global
window.LandmarksVisualizer = LandmarksVisualizer;
