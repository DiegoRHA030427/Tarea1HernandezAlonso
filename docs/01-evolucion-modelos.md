# 1. Evolución de los modelos

## ¿Qué es un modelo de lenguaje (LM)?

Un modelo de lenguaje básicamente es un modelo que calcula qué tan probable es una secuencia de texto. Lo que hacen los modelos de ahora es predecir cuál es el siguiente *token* (una palabra o un pedazo de palabra) según el texto que ya tienen:

```
P(siguiente token | todo lo anterior)
```

Para generar una respuesta completa, el modelo repite esto una y otra vez: predice un token, lo agrega al texto y vuelve a predecir. Algo que me pareció importante es que el modelo no "busca" nada en ningún lado, todo lo que sabe está guardado en sus pesos (parámetros) y en el texto que le mandas.

Más o menos así fue la evolución:

- **N-gramas:** contaban qué tan seguido aparecían grupos de *n* palabras en un montón de texto. El problema es que solo veían unas pocas palabras hacia atrás y si una combinación nunca había salido en los datos, no sabían qué hacer.
- **Redes neuronales (RNN, LSTM):** empezaron a representar las palabras como vectores (*embeddings*) y a leer el texto palabra por palabra. Funcionaban mejor, pero eran lentas porque todo era secuencial y se les "olvidaba" lo que venía mucho antes en el texto.
- **Transformer (2017):** aquí cambió todo. El paper *Attention is all you need* (Vaswani et al., 2017) introdujo el mecanismo de **atención**, donde cada token puede "fijarse" en todos los demás al mismo tiempo. Como se puede hacer en paralelo, se aprovechan muy bien las GPUs y se pueden entrenar modelos enormes.

## De LM a LLM

Un LLM (*Large Language Model*) es un modelo de lenguaje, casi siempre basado en Transformer, pero entrenado con muchísimo texto y con miles de millones de parámetros. La tarea sigue siendo la misma (predecir el siguiente token), lo que cambió fue la escala:

1. Kaplan et al. (2020) vieron que el error del modelo baja de forma bastante predecible si le metes más parámetros, más datos y más cómputo. Eso se conoce como *leyes de escalamiento*.
2. Con GPT-3 (Brown et al., 2020), que tenía 175 mil millones de parámetros, se vio que un modelo así de grande podía resolver tareas nuevas solo con ver unos ejemplos en el prompt, sin volver a entrenarlo (*few-shot learning*).
3. Pero un modelo recién entrenado solo sabe "continuar texto", no seguir instrucciones. Para que se comporte como asistente se le hace un ajuste fino y se usa **RLHF** (aprendizaje por refuerzo con retroalimentación humana), como en InstructGPT (Ouyang et al., 2022). De ahí salen los chatbots que usamos.

La forma en que yo lo entiendo: el preentrenamiento es como si el modelo se leyera toda una biblioteca, y el ajuste por instrucciones es enseñarle a contestarle bien a alguien con lo que leyó.

## Modelos con razonamiento explícito

Son modelos como OpenAI o1, DeepSeek-R1 o los modos de "pensamiento extendido" de Claude y Gemini. La diferencia es que antes de dar la respuesta final generan una cadena de pasos intermedios, como si hicieran el problema en borrador. Así pueden dividir el problema, intentar algo, darse cuenta de que estaba mal y corregirlo.

Algo que hay que dejar claro es que **esto no sale nada más por hacer el modelo más grande**. Un modelo más grande es mejor en general, pero el razonamiento viene principalmente de dos cosas:

**1. Técnicas de entrenamiento.** Primero estuvo el *chain-of-thought prompting* (Wei et al., 2022), que básicamente es pedirle al modelo "piensa paso a paso" y con eso mejoraba, pero eso es solo una forma de escribir el prompt. Los modelos de razonamiento de ahora se entrenan con **aprendizaje por refuerzo** usando problemas donde se puede comprobar si la respuesta está bien, como problemas de matemáticas o código con pruebas unitarias. Si su razonamiento llega a la respuesta correcta, se le "premia", y así aprende a razonar más largo y a revisarse a sí mismo (OpenAI, 2024; DeepSeek-AI, 2025). En el paper de DeepSeek-R1 cuentan que cosas como verificar y reflexionar aparecieron solas gracias a ese entrenamiento, no por el tamaño.

**2. Más cómputo al momento de responder (*test-time compute*).** El modelo usa más tokens "pensando" antes de contestar. OpenAI (2024) reportó que o1 sale mejor entre más tiempo le dejas pensar. Por eso varios de estos modelos tienen un presupuesto de razonamiento que se puede ajustar: más presupuesto significa que tarda más y cuesta más, pero se equivoca menos en problemas difíciles.

Lo comparo con un examen: un modelo grande sin este entrenamiento es como alguien que se memorizó el libro y contesta rapidísimo. Un modelo de razonamiento es alguien al que sí le enseñaron a resolver en borrador y además le dan tiempo de usarlo.

Aun así, todo ese razonamiento sigue siendo **texto**. Por más que "piense", el modelo no puede abrir un archivo ni correr código por sí solo, y eso es justo lo que se ve en el siguiente punto ([02-aislamiento.md](02-aislamiento.md)).

*Referencias: ver la sección de referencias del [README](../README.md#referencias).*
