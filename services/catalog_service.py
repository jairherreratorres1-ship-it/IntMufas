import csv
import re
import requests
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class CatalogoService:
    """
    Maneja la carga de catálogos desde Google Sheets.
    
    Responsabilidades:
    - Descargar CSV desde Google Sheets
    - Parsear datos
    - Permitir búsquedas en catálogos
    """
    
    def __init__(self, catalog_url: str):
        """
        Inicializa el servicio.
        
        Args:
            catalog_url (str): URL de Google Sheets en formato CSV
        """
        self.catalog_url = catalog_url
        
        # Estructuras internas
        self.mufas_map = {}              # {"WN-001": "WN-FALLBACK-1", ...}
        self.supervisores = []           # ["ADMIN", "STEFANNY ANCALLA", ...]
        self.contratas = []              # ["ARKTURIAS", "BELAZA", ...]
        self.nodos = []                  # ["NODO-TEST", "BARRANCO", ...]
        
        # Cargar catálogos automáticamente
        self.cargar_catalogos()
    
    def cargar_catalogos(self) -> bool:
        """
        Descarga catálogos desde Google Sheets.
        
        Returns:
            bool: True si carga exitosa, False si falla
        """
        datos_fallback = """CODIGO,CODIGO ANTIGUO,REFERENCIA,SUPERVISOR,CONTRATA,NODO
WN-FALLBACK-1,WN-FB-001,MUFA DE PRUEBA | WN-128H-SRE025,ADMIN,ARKTURIAS,NODO-TEST
WN-FALLBACK-2,WN-FB-002,MUFA DE PRUEBA 2,STEFANNY ANCALLA,BELAZA,BARRANCO"""
        
        try:
            logger.info(f"⏳ Descargando catálogos desde Google Sheets...")
            response = requests.get(self.catalog_url, timeout=10)
            response.raise_for_status()
            datos_csv = response.text
            logger.info("✅ Catálogos descargados exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Fallo al descargar. Usando datos locales: {e}")
            datos_csv = datos_fallback
        
        # Parsear CSV
        return self._parsear_csv(datos_csv)
    
    def _parsear_csv(self, csv_text: str) -> bool:
        """
        Parsea texto CSV y popula estructuras internas.
        
        Args:
            csv_text (str): Contenido CSV
            
        Returns:
            bool: True si parsea correctamente
        """
        try:
            csv_file = StringIO(csv_text)
            reader = csv.DictReader(csv_file)
            
            temp_mufas = {}
            temp_supervisores = set()
            temp_contratas = set()
            temp_nodos = set()
            
            for row in reader:
                # Código principal
                mufa_principal = row.get("CODIGO", "").strip().upper()
                if not mufa_principal:
                    continue
                
                # Agregar variantes (código antiguo, referencia)
                mufa_ids = [mufa_principal]
                
                mufa_old = row.get("CODIGO ANTIGUO", "").strip().upper()
                if mufa_old and mufa_old != mufa_principal:
                    mufa_ids.append(mufa_old)
                
                # Extraer código de referencia
                referencia = row.get("REFERENCIA", "")
                mufa_ref = self._extraer_codigo_referencia(referencia)
                if mufa_ref and mufa_ref not in (mufa_principal, mufa_old):
                    mufa_ids.append(mufa_ref)
                
                # Mapear todos los IDs a código principal
                for mufa_id in mufa_ids:
                    clean_id = mufa_id.strip('-')
                    if clean_id:
                        temp_mufas[clean_id] = mufa_principal
                
                # Catálogos de opciones
                supervisor = row.get("SUPERVISOR", "").strip().upper()
                if supervisor:
                    temp_supervisores.add(supervisor)
                
                contrata = row.get("CONTRATA", "").strip().upper()
                if contrata:
                    temp_contratas.add(contrata)
                
                nodo = row.get("NODO", "").strip().upper()
                if nodo:
                    temp_nodos.add(nodo)
            
            # Guardar en instancia (en orden alfabético)
            self.mufas_map = temp_mufas
            self.supervisores = sorted(list(temp_supervisores))
            self.contratas = sorted(list(temp_contratas))
            self.nodos = sorted(list(temp_nodos))
            
            logger.info(
                f"✅ Catálogos cargados: "
                f"{len(set(self.mufas_map.values()))} MUFAs, "
                f"{len(self.supervisores)} supervisores"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al parsear CSV: {e}")
            return False
    
    @staticmethod
    def _extraer_codigo_referencia(texto: str) -> str:
        """
        Extrae código MUFA de texto de referencia.
        
        Busca patrones como: "WN-128H-SRE025"
        
        Args:
            texto (str): Texto donde buscar
            
        Returns:
            str: Código extraído o None
        """
        if not texto:
            return None
        
        patron = r'(WN-[A-Z0-9\-]{5,50})'
        matches = re.findall(patron, texto.upper())
        return matches[0] if matches else None
    
    def buscar_mufas(self, query: str, limit: int = 5) -> list:
        """
        Busca MUFAs que contengan el texto de búsqueda.
        
        Ej: buscar_mufas("FALLBACK") → ["WN-FALLBACK-1", "WN-FALLBACK-2"]
        
        Args:
            query (str): Texto a buscar
            limit (int): Máximo de resultados
            
        Returns:
            list: Lista de MUFAs encontradas
        """
        query_upper = query.upper().strip('-')
        
        # Buscar IDs que contengan query
        resultados = [
            mufa_id for mufa_id in self.mufas_map.keys()
            if query_upper in mufa_id
        ]
        
        # Ordenar por longitud (más cortos primero)
        resultados.sort(key=len)
        
        return resultados[:limit]
    
    def buscar_supervisores(self, query: str, limit: int = 5) -> list:
        """
        Busca supervisores que contengan el texto.
        
        Ej: buscar_supervisores("STEF") → ["STEFANNY ANCALLA"]
        
        Args:
            query (str): Texto a buscar
            limit (int): Máximo de resultados
            
        Returns:
            list: Lista de supervisores encontrados
        """
        query_lower = query.lower()
        
        resultados = [
            supervisor for supervisor in self.supervisores
            if query_lower in supervisor.lower()
        ]
        
        return resultados[:limit]
    
    def buscar_nodos(self, query: str, limit: int = 5) -> list:
        """
        Busca nodos que contengan el texto.
        
        Args:
            query (str): Texto a buscar
            limit (int): Máximo de resultados
            
        Returns:
            list: Lista de nodos encontrados
        """
        query_lower = query.lower()
        
        resultados = [
            nodo for nodo in self.nodos
            if query_lower in nodo.lower()
        ]
        
        return resultados[:limit]
    
    def obtener_contratas(self) -> list:
        """Retorna lista de contratas (para mostrar todas)"""
        return self.contratas
    
    def mufa_existe(self, mufa: str) -> bool:
        """
        Verifica si una MUFA existe en el catálogo.
        
        Args:
            mufa (str): Código MUFA a verificar
            
        Returns:
            bool: True si existe
        """
        return mufa.upper() in self.mufas_map
    
    def obtener_mufa_principal(self, mufa_id: str) -> str:
        """
        Obtiene el código principal de una MUFA.
        
        Si pasas "WN-FB-001", te devuelve "WN-FALLBACK-1"
        
        Args:
            mufa_id (str): Código MUFA (puede ser variante)
            
        Returns:
            str: Código principal
        """
        return self.mufas_map.get(mufa_id.upper(), mufa_id.upper())