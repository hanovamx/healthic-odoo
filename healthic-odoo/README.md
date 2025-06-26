# 🏥 Healthic - Sistema de Gestión de Instrumental Médico

## 📋 Descripción

Sistema completo para la digitalización del proceso de recepción, seguimiento, control y entrega de instrumental médico esterilizado. Garantiza trazabilidad total, cumplimiento normativo y eficiencia operativa.

## ✅ Estado del Proyecto

- ✅ **FASE 1 COMPLETADA** - Modelado de Datos (Backend)
- ✅ **FASE 2 COMPLETADA** - Vistas y UI para Operadores

## 🎯 Funcionalidades Implementadas

### 📊 Dashboard Principal (Vista Kanban)
- Visualización en tiempo real por estado de orden
- Colores dinámicos según etapa del proceso
- Botones de acción rápida contextuales
- Información clave: cliente, STU, fecha recepción

### 📋 Gestión de Órdenes (Vista Formulario)
- **Pestaña General**: Datos básicos y recepción
- **Pestaña Lavado**: Proceso y métodos aplicados
- **Pestaña Empaque**: Asignación y procedimientos
- **Pestaña Esterilización**: Métodos y validaciones
- **Pestaña Entrega**: Evidencias y confirmación

### 🔍 Trazabilidad Detallada
- Seguimiento individual por instrumento
- Validación de métodos compatibles
- Registro de responsables por proceso
- Cálculos automáticos de STU y duración

### 📱 Optimización para Operadores
- Interfaces tablet-friendly (10" pantallas)
- Widgets especializados: toggles, radio buttons
- Validaciones visuales en tiempo real
- Accesos rápidos para tareas frecuentes

## 🏗️ Arquitectura del Sistema

### Modelos Implementados
1. **hospital.client** - Clientes hospitalarios
2. **instrument.method** - Métodos de lavado/esterilización
3. **instrument.catalog** - Catálogo de instrumentos
4. **instrument.order** - Órdenes de procesamiento
5. **instrument.order.line** - Líneas de detalle

### Vistas Creadas
- **8 vistas Kanban** para dashboards interactivos
- **5 vistas Formulario** con pestañas organizadas
- **5 vistas Tree/List** para consultas masivas
- **5 vistas Search** con filtros avanzados
- **20+ acciones** y menús organizados

## 🎛️ Menús Principales

### ⚡ Accesos Rápidos
- ➕ Nueva Orden
- ⏳ Órdenes Pendientes
- 🔄 En Proceso
- ✅ Listo para Entrega

### 📋 Operaciones
- 🎛️ Dashboard de Órdenes
- 📊 Todas las Órdenes
- 🔍 Detalle de Instrumentos

### ⚙️ Configuración
- 🏥 Catálogo de Instrumentos
- 🏢 Clientes Hospitalarios
- 🔧 Métodos de Proceso

### 📈 Reportes
- 👥 Por Cliente
- 📅 Por Fecha
- 🔍 Trazabilidad

## 🔧 Instalación

1. Copiar el módulo a `addons/healthic-odoo/`
2. Actualizar lista de aplicaciones
3. Instalar "Healthic - Gestión de Instrumental Médico"
4. Los datos iniciales se cargan automáticamente

## 📊 Datos Iniciales Incluidos

### Métodos Preconfigurados
**Lavado:**
- Lavado Manual
- Lavado Ultrasónico  
- Lavadora Automática

**Esterilización:**
- Autoclave Vapor
- Peróxido de Hidrógeno
- Plasma Gas
- Óxido de Etileno
- Calor Seco

### Datos Demo
- 3 clientes hospitalarios
- 5 instrumentos de ejemplo
- Relaciones método-instrumento configuradas

## 🎨 Características UX

### Widgets Especializados
- `boolean_toggle` para campos sí/no
- `radio` horizontal para selecciones
- `badge` para estados visuales
- `datetime` para fechas/horas
- `many2many_tags` para relaciones

### Validaciones Visuales
- Campos obligatorios destacados
- Estados disponibles dinámicos
- Decoraciones por estado
- Alertas de compatibilidad

### Optimización Tablet
- Botones grandes con iconos
- Sin scroll horizontal
- Formularios colapsables
- Navegación intuitiva

## 🔒 Seguridad y Permisos

- **Usuarios normales**: Lectura/escritura sin eliminación
- **Administradores**: Acceso completo
- **Validaciones de negocio**: 15+ restricciones implementadas
- **Auditoría**: Seguimiento de cambios con Chatter

## 🚀 Próximas Fases

### Fase 3 - Funcionalidades Avanzadas
- Sistema de códigos de barras
- Notificaciones automáticas
- Integración con balanzas/sensores
- API para dispositivos móviles

### Fase 4 - Reportes Avanzados
- Dashboard ejecutivo
- Análisis de tendencias
- Indicadores KPI
- Exportación automática

## 👥 Soporte

Desarrollado por **Healthic** - Especialistas en soluciones hospitalarias

Para soporte técnico o consultas: info@healthic.com

---

**Versión:** 1.0.0  
**Compatible con:** Odoo 18  
**Licencia:** Propietaria Healthic

## Características Principales

### Modelos Principales
- **Hospital Client**: Gestión de clientes hospitalarios
- **Instrument Catalog**: Catálogo de instrumentos médicos
- **Instrument Method**: Métodos de lavado y esterilización
- **Instrument Order**: Órdenes de procesamiento de instrumental
- **Instrument Order Line**: Líneas de detalle de las órdenes
- **Surgery Type**: Tipos de cirugía con instrumentos predeterminados

### Funcionalidades de Seguridad y Archivo

#### Sistema de Archivo
- Todos los modelos principales incluyen funcionalidad de archivo (campo `active`)
- Los registros se pueden archivar en lugar de eliminar para mantener la integridad de datos
- Filtros en las vistas para mostrar registros activos/inactivos

#### Protección de Eliminación
- **Instrument Order Line**: No se puede eliminar si:
  - La orden está en estado avanzado (en_lavado, empaque, esterilizado, entregado)
  - Tiene datos de procesamiento (fechas, métodos aplicados)
- **Surgery Type Instrument**: No se puede eliminar si hay órdenes que usan ese tipo de cirugía

#### Valores por Defecto
- Campo `entregado_en` en `instrument.order.line` tiene valor por defecto 'area_negra' (opcional)
- Campo `estado_entrega` tiene valor por defecto 'completo' (opcional)
- Todos los campos requeridos tienen valores por defecto apropiados

### Permisos de Acceso
- **Usuarios**: Pueden leer, crear y modificar registros, pero no eliminar
- **Administradores**: Acceso completo incluyendo eliminación
- Permisos específicos para cada modelo

## Instalación

1. Copiar el módulo al directorio `addons` de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Healthic Odoo"
4. Configurar los permisos de acceso según sea necesario

## Uso

### Crear una Orden
1. Ir a "Órdenes de Instrumental" > "Crear"
2. Seleccionar el cliente hospitalario
3. Agregar instrumentos desde el catálogo o tipos de cirugía predeterminados
4. Cada línea de instrumento se crea automáticamente con valores por defecto

### Procesar una Orden
1. Cambiar el estado de la orden según el proceso
2. Completar los datos específicos en cada línea de instrumento
3. Los campos requeridos se completan automáticamente con valores por defecto

### Archivar Registros
- Usar la funcionalidad de archivo en lugar de eliminar
- Los registros archivados se pueden restaurar si es necesario
- Mantiene la integridad referencial de los datos

## Solución de Problemas

### Error: "No se pudo completar la operación"
- **Crear/Actualizar**: Verificar que todos los campos requeridos tengan valores
- **Eliminar**: Usar la funcionalidad de archivo en lugar de eliminar

### Error: "Campo obligatorio no configurado"
- Los campos requeridos ahora tienen valores por defecto
- Si persiste el error, verificar que el módulo se haya actualizado correctamente

## Actualizaciones Recientes

### v1.1 - Correcciones de Acceso
- ✅ Agregado valor por defecto al campo `entregado_en` (ahora opcional)
- ✅ Campo `estado_entrega` ahora es opcional con valor por defecto
- ✅ Implementado sistema de archivo para todos los modelos
- ✅ Protección de eliminación para registros con dependencias
- ✅ Mejorados los permisos de acceso
- ✅ Agregados filtros para registros activos/inactivos

## Soporte
Para soporte técnico o reportar problemas, contactar al equipo de desarrollo. 