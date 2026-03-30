# Configuración de Dominio Personalizado

Esta guía describe cómo configurar un dominio personalizado (ej: `meacore.ai`) para el proyecto desplegado en Vercel.

## Pasos

1.  **Adquirir un Dominio:**
    *   Compra el dominio deseado a través de un registrador de dominios como GoDaddy, Namecheap, o Google Domains.

2.  **Añadir Dominio en Vercel:**
    *   Navega al dashboard de tu proyecto en Vercel.
    *   Ve a la pestaña **Settings -> Domains**.
    *   Añade tu dominio personalizado (ej: `meacore.ai`).
    *   Vercel proporcionará los registros DNS (ya sea `A` o `CNAME`) que necesitas configurar en tu registrador de dominios.

3.  **Configurar DNS:**
    *   Inicia sesión en el panel de control de tu registrador de dominios.
    *   Ve a la sección de gestión de DNS para tu dominio.
    *   Añade los registros proporcionados por Vercel.
        *   Para un dominio raíz (`meacore.ai`), normalmente se usa un registro `A`.
        *   Para un subdominio (`www.meacore.ai`), se usa un registro `CNAME`.
    *   Guarda los cambios. La propagación de DNS puede tardar desde unos minutos hasta 48 horas.

4.  **Verificación:**
    *   Una vez que los DNS se hayan propagado, Vercel verificará automáticamente la configuración y emitirá un certificado SSL para tu dominio.
    *   El estado en el dashboard de Vercel cambiará a "Valid Configuration".

¡Listo! Tu aplicación será accesible a través de tu dominio personalizado.
