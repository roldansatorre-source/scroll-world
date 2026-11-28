# Baremo — landing "scroll world"

Página de scroll en la que la cámara recorre 6 escenas de arcilla mate low-poly
(cámara isométrica fija, luz neutra de oficina). Generada con el skill `scroll-world`.

## Ver en local

```bash
cd baremo/site && python3 -m http.server 8000   # abrir http://localhost:8000
```

Todo lo necesario está en `site/` (HTML + `scrub-engine.js` + `assets/`), sin dependencias.

## Qué hay

| Escena | Etiqueta | Vídeo escritorio | Vídeo móvil (9:16) | Imagen fija |
|---|---|---|---|---|
| 1 | Para gestorías y consultoras | `vid/s1.mp4` | `vid/s1-m.mp4` | `s1.webp` |
| 2 | Paso 1 | `vid/s2.mp4` | `vid/s2-m.mp4` | `s2.webp` |
| 3 | Paso 2 | `vid/s3.mp4` | `vid/s3-m.mp4` | `s3.webp` |
| 4 | Paso 3 | `vid/s4.mp4` | `vid/s4-m.mp4` | `s4.webp` |
| 5 | Paso 4 | `vid/s5.mp4` | `vid/s5-m.mp4` | `s5.webp` |
| 6 | Auditoría gratis (CTA) | `vid/s6.mp4` | `vid/s6-m.mp4` | `s6.webp` |

- Cada tramo arranca del último fotograma real del anterior: el recorrido no tiene cortes.
- `prefers-reduced-motion`: no se cargan vídeos; se muestran las imágenes fijas
  (`sN.webp`, y en móvil `sN-ms.webp`) con los mismos textos.
- Los enlaces del botón "Sube tu cartera" y "Ver precios" están a `#`: pon las URLs reales en `site/index.html`.

## Arreglos hechos en edición (sin créditos extra)

- Escena 3 escritorio: corte seco a 1,5 s → fundido de 0,8 s.
- Escena 4 escritorio: salto de zoom a 5,3 s → fundido de 0,6 s.
- Escena 4 móvil: recortado a 3,1 s para que no se lea texto inventado en las fichas.
- Escenas 4–6 móvil: fondo con "fantasmas" de compresión → aplanado (`tools/clean_bg.py`).

## Revisión

Capturas en `qa/`. Sin errores de consola; vídeos con seek completo; móvil sirve los
clips verticales 720×1280; sin movimiento carga solo imágenes.
