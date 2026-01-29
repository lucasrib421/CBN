import { useState, useEffect } from 'react'; 
import { NewsService } from '../services/newsService';
import type { Menu } from '../types'; // Nosso tipo

export const Header = () => {
const [menuData, setMenuData] = useState<Menu | null>(null);

useEffect(()=>{
    const fetchMenu = async () => {
      try {
        const menus = await NewsService.getMenus();
        
        console.log("O que veio da API:", menus); // Dica: Olhe o Console do navegador (F12)

        if (menus.length > 0) {
          setMenuData(menus[0]); 
        }
      } catch (error) {
        console.error("Deu erro ao buscar:", error);
      }
    };

    // Executamos a função imediatamente
    fetchMenu();
},[]);


 return (
    <header style={{ background: '#000', padding: '0', color: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '60px' }}>
        
        {/* Lado Esquerdo: Logo Transformado em Link */}
        <a 
          href="/" 
          style={{ 
            textDecoration: 'none', // Remove o sublinhado do link
            display: 'flex', 
            alignItems: 'center', 
            height: '100%',
            color: 'white', // Garante que o texto "Clone" continue branco
            cursor: 'pointer'
          }}
        >
          {/* 2. Imagem cbn*/}
          <img 
            src="/images/CBN_LOGO.png"  
            alt="Logo CBN"
            style={{ 
              height: '60px', // Ajuste a altura conforme necessário
              width: 'auto',  // Mantém a proporção correta
              objectFit: 'contain',
              marginRight: '15px' 
            }} 
          />
          {/* Texto Clone */}
          <span style={{ fontSize: '0.9rem', opacity: 0.8, textTransform: 'uppercase', letterSpacing: '1px' }}>
            Corrupção Brasileira News
          </span>
        </a>

        {/* Lado Direito: Navegação */}
        <nav>
          {menuData ? (
            <ul style={{ listStyle: 'none', display: 'flex', gap: '25px', margin: 0, padding: 0 }}>
              {menuData.items.map((item) => (
                <li key={item.id}>
                  <a 
                    href={item.url} 
                    style={{ 
                      color: 'white', 
                      textDecoration: 'none', 
                      fontWeight: 'bold', 
                      fontSize: '0.85rem',
                      textTransform: 'uppercase',
                      transition: 'color 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.color = '#b91c1c'}
                    onMouseOut={(e) => e.currentTarget.style.color = 'white'}
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <span style={{ fontSize: '0.8rem', color: '#666' }}>Carregando...</span>
          )}
        </nav>

      </div>
    </header>
  );
};