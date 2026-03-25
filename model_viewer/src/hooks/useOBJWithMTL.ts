import { useLoader } from '@react-three/fiber';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { MTLLoader } from 'three/addons/loaders/MTLLoader.js';
import * as THREE from 'three';

class OBJMTLLoader {
  load(
    objUrl: string,
    onLoad: (object: THREE.Group) => void,
    _onProgress?: (event: ProgressEvent) => void,
    onError?: (err: unknown) => void
  ) {
    const baseUrl = objUrl.substring(0, objUrl.lastIndexOf('/') + 1);
    const mtlLoader = new MTLLoader();
    mtlLoader.setPath(baseUrl);
    const objLoader = new OBJLoader();

    const mtlFile = objUrl.split('/').pop()?.replace('.obj', '.mtl') ?? 'model.mtl';
    const objFile = objUrl.split('/').pop() ?? 'model.obj';

    mtlLoader.load(
      mtlFile,
      (materials) => {
        materials.preload();
        objLoader.setMaterials(materials);
        objLoader.setPath(baseUrl);
        objLoader.load(objFile, onLoad, undefined, onError);
      },
      undefined,
      onError
    );
  }
}

export function useOBJWithMTL(url: string) {
  return useLoader(OBJMTLLoader, url);
}
