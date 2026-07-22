//Based on Perlin-like Noise in C++
//https://www.youtube.com/watch?v=6-0UaeJBumA
const int RAND_MAX = 1073741823;
const int SCREEN_HEIGHT = 900;
const int SCREEN_WIDTH = 1600;
class PerlinNoise {
  array<float> noiseSeed1d;
  array<float> perlinNoise1d;
  uint octaves;
  uint outputSize;
  int nMode;
  float scale;

  PerlinNoise(int outSiz = 255, uint nOctaves = 8, float sc = 2.0f, int nmode = 1) {
    outputSize = outSiz;
    scale = sc;
    setOctaves(nOctaves);
    seed();
  }

  array<float> PerlinNoise1D() {
    array<float> output(outputSize);

    for(uint x = 0; x < outputSize; x++) {
      float fNoise = 0.0f;
      float fScale = 1.0f;
      float fScaleAcc = 0.0f;

      for(uint o = 0; o < octaves; o++) {
        uint nPitch = outputSize >> o;
        uint nSample1 = (x / nPitch) * nPitch;
        uint nSample2 = (nSample1 + nPitch) % outputSize;

        float fBlend = float(x - nSample1) / float(nPitch);
        float fSample = (1.0f - fBlend) * noiseSeed1d[nSample1] + fBlend * noiseSeed1d[nSample2];
        fNoise += fSample * fScale;
        fScaleAcc += fScale;
        fScale /= scale;
      }

      // Scale to seed range
      if(fScaleAcc > 0) {
        output[x] = (fNoise / fScaleAcc);
      }
    }
    return output;
  }

  void seed() {
    //srand(timestamp_now()); USE MSG's RANDOMIZER AND STEP IT BEFORE THIS
    noiseSeed1d = array<float>(0);
    
    for(uint i = 0; i < outputSize; i++) {
      noiseSeed1d.insertLast(rand() /float(RAND_MAX));
    }
  }

  void setOctaves(uint octs) {
    octaves = octs;
  }

  void setOutSize(uint outSize) {
    outputSize = outSize;
  }

  void setScale(float sca) {
    scale = sca;
  }

  void setMode(int m) {
    nMode = m;
  }
}


class PerlinNoise2 {
  array<float> noiseSeed2d;
  array<float> perlinNoise2d;
  uint octaves = 1;
  uint outputWidth;
  uint outputHeight;
  float scale;

  PerlinNoise2(uint outWidth = 256, uint outHeight = 256, uint nOctaves = 8, float sc = 2.0f) {
    outputWidth = outWidth;
    outputHeight = outHeight;
    scale = sc;
    setOctaves(nOctaves);
    seed();
  }

  array<float> generateNoise2d() {
    array<float> fOutput(outputWidth * outputHeight);
   for (int x = 0; x < outputWidth; x++) {
			for (int y = 0; y < outputHeight; y++)
			{				
				float fNoise = 0.0f;
				float fScaleAcc = 0.0f;
				float fScale = 1.0f;
				for (int o = 0; o < octaves; o++)
				{
          
					int nPitch = outputWidth >> o;
          nPitch = nPitch == 0 ? 1 : nPitch;
					int nSampleX1 = (x / nPitch) * nPitch;
					int nSampleY1 = (y / nPitch) * nPitch;

					int nSampleX2 = (nSampleX1 + nPitch) % outputWidth;
					int nSampleY2 = (nSampleY1 + nPitch) % outputWidth;

					float fBlendX = float(x - nSampleX1) / float(nPitch);
					float fBlendY = float(y - nSampleY1) / float(nPitch);
          
					float fSampleT = (1.0f - fBlendX) * noiseSeed2d[nSampleY1 * outputWidth + nSampleX1] + fBlendX * noiseSeed2d[nSampleY1 * outputWidth + nSampleX2];
					float fSampleB = (1.0f - fBlendX) * noiseSeed2d[nSampleY2 * outputWidth + nSampleX1] + fBlendX * noiseSeed2d[nSampleY2 * outputWidth + nSampleX2];
          
					fScaleAcc += fScale;
					fNoise += (fBlendY * (fSampleB - fSampleT) + fSampleT) * fScale;
					fScale = fScale / scale;
          
				}
				// Scale to seed range
				fOutput[y * outputWidth + x] = fNoise / fScaleAcc;
			}
    }
    return fOutput;
  }

  void seed() {
    srand(timestamp_now());
    //Be sure to use MSG's rand script and step it before using this to seed
     noiseSeed2d = array<float>(0);
    for(uint i = 0; i < outputWidth * outputHeight; i++) {
      noiseSeed2d.insertLast(rand() /float(RAND_MAX));
    }
  }

  void seed(uint seedval) {
    srand(seedval);
    //Be sure to use MSG's rand script and step it before using this to seed
     noiseSeed2d = array<float>(0);
    for(uint i = 0; i < outputWidth * outputHeight; i++) {
      noiseSeed2d.insertLast(rand() /float(RAND_MAX));
    }
  }

  void setOctaves(uint octs) {
    octaves = octs;
  }

  void setOutSize(uint outWidth, uint outHeight) {
    outputWidth = outWidth;
    outputHeight = outHeight;
  }

  void setScale(float sca) {
    scale = sca;
  }
}