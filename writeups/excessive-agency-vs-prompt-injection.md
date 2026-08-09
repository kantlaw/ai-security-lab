## Excessive agency vs prompt injection lo que aprendí atacando escáneres con IA

## La distinción

|                                         | Prompt injection                                          | Excessive agency                                                                           |
| --------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Qué pasa**                            | El atacante inyecta instrucciones que el modelo obedece   | El agente decide actuar por su cuenta sobre lo que encuentra                               |
| **¿Hay instrucción maliciosa?**         | Sí                                                        | No                                                                                         |
| **Ejemplo**                             | Escape de contexto + orden explícita de borrar al usuario | Se pide solo el HTML del panel; el agente sigue el enlace de borrado por iniciativa propia |
| **Mitigación correcta**                 | Filtrado, delimitación, instruction hierarchy             | Acotar permisos y exigir confirmación humana                                               |
| **¿Lo detiene un filtro de inyección?** | Parcialmente                                              | No                                                                                         |

**1. Mapear agencia antes que prompts**

El lab 4 no se resolvió por el payload sino porque el escáner tenía credenciales de Carlos, `send_request` y alcance a `192.168.0.0/24`. El payload final fue una línea pidiendo el HTML del panel.

_Implicación:_ la primera pregunta de si estaria en una auditoría no es "¿se puede inyectar?" sino qué herramientas tiene tiene el LLM con qué identidad corre osea qué alcanza en red y qué acciones son problematicas

---

**2. Combinaciones tóxicas de herramientas**

En el lab de exfiltración, el escáner podía leer la API key (contexto) y escribir comentarios (`POST /post/comment`). Ninguna capacidad es peligrosa sola; juntas son un canal de exfiltración sin necesidad de red externa.

_Implicación:_ auditar pares de herramientas no herramientas sueltas. Leer datos sensibles + escribir donde el atacante lee = fuga por ejemplo a la hora de pedirle algo al LLM podria mostrar información de mas por ejemplo la api key de alguien

---

**3. El informe del agente no es evidencia**

Cuando estaba haciendo el lab el LLM me dijo que había cumplido las acciones pero mintió en las dos direcciones:

- _Command injection: devolvió "correo inválido" y el archivo ya estaba borrado. `$()` ejecutó antes de que fallara la validación del email.
- _Lab 4: reportó _"successfully exploited... delete users"_ y el lab seguía sin resolver.

_Implicación:_ verificar por canal independiente o saber si realmente ejecuto la peticion

---

**4. Todo campo del contexto es superficie**

En el lab del escáner, firmar como `Administrator` en vez de `developer` cambió el resultado. El nombre del autor también entra al contexto ya que podria tomar esto como una figura de autoridad ya que podria pensar que no tomaba al developer como alguien privilegiado

_Implicación:_ auditar todos los campos que llegan al modelo autor, fecha, título, metadatos  no solo el cuerpo del texto.

## Cómo llegué ahí

_Bueno llegue de esa forma mediante sobre que se podían dejar comentarios en los blogs como el escáner analizaba todo lo que era la pagina este podia tomar el input o prompt y ejecutar inconscientemente lo que se le pide por ejemplo si puede tambien publicar comentarios se podria aprovechar eso para revelar información privada_

---

**5. Cuantificar**

El mismo payload falló y funcionó en intentos distintos. En el lab de defensas, ocho variantes antes de acertar; en el 4, resultados oscilantes con el mismo texto.

_Implicación:_ un hallazgo sin tasa de éxito no es reproducible. "Funciona el 60%, n=20" es defendible; "funciona" se cierra como no reproducible.

---

**6. Descomponer la cadena**

Pedir enumeración + bypass + borrado en un payload fallaba. Salió con un paso por escaneo: localizar el host → confirmar el bypass → ejecutar.

_Implicación:_ cada instrucción atómica es plausible por separado; la cadena completa parece un ataque ya que cuando yo lo intente el LLM me lo tomaba como malicioso por lo cual trate de realizar diferentes peticiones con otros contextos y tomandolo por partes para enumerar poco a poco

## Cómo llegué ahí

Trataba de enviar el mismo payload pero no funcionaba el LLM me lo tomaba como injection por lo cual tuve que empezar a buscar la forma de reducir las palabras y las cosas que mencionaba en el prompt para que el LLM no lo tomara como intento de ataque por ende trate que fuese paso por paso para poder enumerar quizas de forma mas lenta pero era efectiva_

---

**7. El pretexto aburrido gana**

`----SYSTEM MESSAGE----` firmado como Administrator fue detectado como social engineering y reportado. Lo que funcionó: `SECURITY ISSUE FOUND!` en formato de reporte técnico, mimetizando la salida del propio escáner.

_Implicación:_ la evasión efectiva no es más autoridad, es menos fricción.

## Cómo llegué ahí

_Si se utiliza un preetexto múltiples veces el LLM lo puede tomar también como social engineering o tipo de ataque por lo cual habría que probar diferente pretextos ya sea como si fuera en formato de reporte técnico o mensaje que no salten las alertas
