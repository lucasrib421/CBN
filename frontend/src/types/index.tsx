//Aqui irei traduzir os dados json que o docker manda para o typescript ler, 
// a estrutura de dados que vao ser traduzidos foi criada no:
//  CBN\homeNews\serializers.py 


// --- Blocos Básicos ---

export interface Media{
    id: number;
    title: string;
    file: string;
    alt_text?: string; // o "?" quer dizer que podemos receber ele vazio
    image_type: string;

}

export interface Author{
    id: number;
    name: string;
    bio?: string;
    avatar?: Media; // usamos a interface criada anteriomente 
}

export interface Category{
    id: number;
    name: string;
    slug: string; // O Slug pega o título, remove acentos, troca espaços por traços (-) e deixa tudo minúsculo
    color?: string; // recebe em hexadecimal 
}

export interface Tag{
    id: number;
    name: string;
    slug: string;
}

// --- Notícias ---

export interface PostSummary{
    id: number;
    title: string;
    subtitle: string;
    slug: string;
    cover_image?: Media;
    author: Author;
    categories: Category[]; // o []porque pode ter varias categorias
    published_at: string;
    reading_time?: number;
    }

    export interface PostDetail extends PostSummary{ // heranca é tudo que post sumary mais algumas coisas que tem no PostDetailSerializer
        content: string;
        tags: Tag[];
        created_at: string;
        updated_at: string;
    }
// --- Estrutura da Home ---

    export interface HomeSectionItem{
        id: number;
        order: number;
        post: PostSummary;
    }

    export interface HomeSection{
        id: number;
        title: string;
        order: number;
        section_type: 'HERO' | 'GRID' | 'LIST' | 'SIDEBAR';
        items: HomeSectionItem[]; // Uma seção tem vários itens (notícias)
    }

// --- Menus ---

export interface MenuItem{
    id:number;
    label: string;
    url: string;
    target?: '_self' | '_blank';
    order: number;
    children?: MenuItem[];
}

export interface Menu{
    id: number;
    title: string;
    slug: string;
    items: MenuItem[];
}