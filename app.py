from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect, session
import os
from datetime import datetime
import random
from flask_compress import Compress
from flask_caching import Cache

app = Flask(__name__)

# Enable compression
Compress(app)

# Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Production configurations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/javascript', 'application/javascript']

# Secret key for session
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Initialize download counts with realistic numbers
SAMPLE_SOFTWARE = [
    {
        "id": "windows-11-22h2",
        "name": "Windows 11 22H2",
        "version": "22H2 16-in-1",
        "size": "5.28 GB",
        "category": "Software",
        "description": "Windows 11 22H2 16-in-1 Edition with latest updates. Features include: • Multiple editions in one package (Pro, Home, Enterprise) • Latest security updates and patches included • Modern interface with enhanced productivity features • DirectStorage and Auto HDR for gaming • Android app support through Amazon Appstore • Improved touch, pen, and voice inputs • Enhanced snap layouts and snap groups",
        "downloads": random.randint(2000, 4000),
        "image_url": "https://cdn.windowsreport.com/wp-content/uploads/2021/06/windows-11-2.jpg",
        "download_links": {
            "mega": "https://mega.nz/file/example-link-1",
            "gdrive": "https://drive.google.com/file/example-link-2"
        }
    },
    {
        "id": "visual-studio-2022",
        "name": "Visual Studio 2022 Community",
        "version": "17.8.3",
        "size": "2.5 GB",
        "category": "Development",
        "description": "Visual Studio 2022 Community Edition - The latest IDE from Microsoft. Features include: • Full-featured IDE for C++, C#, Python, and more • Built-in Git integration • IntelliSense code completion • Live Share for real-time collaboration • Cross-platform development support",
        "downloads": 1205,
        "image_url": "https://visualstudio.microsoft.com/wp-content/uploads/2021/10/Product-Icon.svg",
        "download_links": {
            "official": "https://visualstudio.microsoft.com/thank-you-downloading-visual-studio"
        }
    },
    {
        "id": "adobe-photoshop",
        "name": "Adobe Photoshop",
        "category": "Software",
        "version": "2024",
        "size": "3.2 GB",
        "date_added": "2024-12-20",
        "description": """Reimagine reality with Photoshop. Create stunning designs with intuitive tools and templates. Features include:
• Professional photo editing and retouching
• Symmetry mode for perfect patterns
• Content-Aware Fill with Adobe Sensei
• Frame tool for easy image placement
• 1,000+ brushes from Kyle T. Webster
• Complete set of professional design tools""",
        "external_url": "https://mega.nz/file/MygklQKZ#e6RqQdctHp5Yp7DTlthCcjZp-QVN2yCJ-C0AIx7DaDQ",
        "virustotal_links": [
            "https://www.virustotal.com/gui/file/3b9dabd99dc58a5242616cb6d1d876bca3046119a9b150c7d7868bf02202ea82",
            "https://www.virustotal.com/gui/file/b3506f660a3395674225893af2df056c338006d781c86f2fe05ef27130bd7c3c"
        ],
        "downloads": random.randint(1000, 3000),
    },
    {
        "id": "windows-10-pro",
        "name": "Windows 10 Pro",
        "category": "Software",
        "version": "1709 (Build 16299.98)",
        "size": "4.3 GB",
        "date_added": "2024-12-20",
        "description": "Pre-activated Windows 10 Pro. No extra activation tools required. Features professional-grade security and business tools. Easy installation: just burn/mount and install.",
        "external_url": "https://mega.nz/file/zhcGQDjB#_BWULV3SvMM3_1t8C04LwebDTs4FeLYztAL5BIYgVcg",
        "store_url": "https://www.microsoft.com/en-us/store/d/windows-10-pro/df77x4d43rkt",
        "downloads": random.randint(1500, 3500),
    },
    {
        "id": "windows-11-dev-build",
        "name": "Windows 11 Dev Build",
        "category": "Software",
        "version": "21996.1",
        "size": "4.9 GB",
        "date_added": "2024-12-20",
        "description": "Windows 11 Development Build with Office 2019 included. Features a modern interface, improved productivity tools, and enhanced security features.",
        "external_url": "https://mega.nz/file/79d1EaQa#v2eylQP2jn_7LZTEi5UhNgCg8gbEbdO6brSNv3MWi5E",
        "downloads": random.randint(1000, 3000),
    },
    {
        "id": "avg-antivirus-free",
        "name": "AVG Antivirus Free",
        "category": "Software",
        "version": "2024",
        "size": "512 MB",
        "date_added": "2024-12-20",
        "description": "Free antivirus protection against viruses, malware, and ransomware.",
        "external_url": "https://download.cnet.com/avg-antivirus-free/3001-2239_4-10320142.html?dt=internalDownload",
        "downloads": random.randint(2000, 4000),
    },
    {
        "id": "video-analyzer",
        "name": "Video Analyzer",
        "category": "Software",
        "version": "1.0",
        "size": "15.2 MB",
        "date_added": "2024-12-19",
        "description": "Powerful video analysis tool for content creators and editors.",
        "filename": "video-analyzer.rar",
        "downloads": random.randint(500, 1500),
    },
    {
        "id": "dying-light-2-stay-human",
        "name": "Dying Light 2 Stay Human",
        "category": "Games",
        "version": "v1.19.0",
        "size": "63 GB",
        "date_added": "2024-12-20",
        "downloads": random.randint(1000, 3000),
        "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202107/3100/HO8vkO9pfXhwbHi5WHECQJdN.png",
        "screenshots": [
            "https://cdn.cloudflare.steamstatic.com/steam/apps/534380/ss_8a998c75c26b5d45893a0e815a2a9820b8b0c42e.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/534380/ss_a3ddf22d9ebf3c0c96d0da2a49c19efb02a9cc5a.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/534380/ss_c0c2f6c13d51c4c9c6b89cfc3833975c3c066da6.jpg"
        ],
        "description": """Over twenty years ago in Harran, we fought the virus—and lost. Now, we're losing again. The City, one of the last large human settlements, is torn by conflict. Civilization has fallen back into the Dark Ages. And yet, we still have hope.

Features:
• Full Version + Co-op
• All DLCs included
• Bonus Content included
• Released By: Goldberg+SSE+Nemertingas/TENOKE

System Requirements:
• OS: Windows 7
• CPU: Intel Core i3-9100 / AMD Ryzen 3 2300X
• RAM: 8 GB
• GPU: NVIDIA GeForce GTX 1050 Ti / AMD Radeon RX 560 (4GB VRAM)
• Storage: 63 GB""",
        "genre": ["Action", "Adventure", "RPG"],
        "developer": "Techland",
        "download_links": {
            "1fichier": "https://1fichier.com/?uo4m6rvfxx0okyw8l5ki",
            "gofile": "https://gofile.io/d/QuUrVk"
        }
    },
    {
        "id": "elden-ring",
        "name": "Elden Ring",
        "category": "Games",
        "version": "Latest Version + DLC",
        "size": "80 GB",
        "date_added": "2024-12-20",
        "downloads": random.randint(2000, 4000),
        "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202110/2000/phvVT0qZfcRms5qDAk0SI3CM.png",
        "screenshots": [
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/ss_e80a907c2c43337e53316c71555c3c3035a1343e.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/ss_c372274833ae6e5437b952fa1979430546a43ad9.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1245620/ss_d1a8f0a8a3655f18548068d675e2e65f6c419a7c.jpg"
        ],
        "description": """The new fantasy action RPG. Rise, Tarnished, and be guided by grace to brandish the power of the Elden Ring and become an Elden Lord in the Lands Between.

Features:
• A Vast World Full of Excitement
• Vast world with open fields and huge dungeons seamlessly connected
• Complex and three-dimensional designs
• Customize character appearance, weapons, armor, and magic
• Develop your character according to your play style

Includes:
• Full Game + All DLCs
• Pre-order bonuses
• Digital Artbook
• Original soundtrack

System Requirements:
• OS: Windows 10/11
• CPU: Intel Core i5/AMD Ryzen 5
• RAM: 12 GB
• GPU: NVIDIA GeForce GTX 1060 / AMD Radeon RX 580
• Storage: 80 GB""",
        "genre": ["Action", "RPG", "Open World"],
        "developer": "FromSoftware",
        "download_links": {
            "gofile": "https://gofile.io/d/S683NC"
        }
    },
    {
        "id": "red-dead-redemption-2",
        "name": "Red Dead Redemption 2",
        "category": "Games",
        "version": "Latest Version + Steam Pre-Installed",
        "size": "125 GB",
        "date_added": "2024-12-20",
        "downloads": random.randint(2000, 4000),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/header.jpg",
        "screenshots": [
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/ss_66b553f4c209476d3e4ce25fa4714002cc914c4f.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/ss_d1a8f0a8a3655f18548068d675e2e65f6c419a7c.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1174180/ss_668dafe477743f8b50b818d5bbfcec669e9ba93e.jpg"
        ],
        "description": """Arthur Morgan and the Van der Linde gang are on the run. With federal agents and the best bounty hunters in the nation massing on their heels, the gang must rob, steal and fight their way across the rugged heartland of America in order to survive. As deepening internal divisions threaten to tear the gang apart, Arthur must make a choice between his own ideals and loyalty to the gang who raised him.

Features:
• Full Story Mode content
• Fully-featured Photo Mode
• Free access to Red Dead Online
• Enhanced PC Graphics and Performance
• Create businesses: Trader, Collector, Moonshiner
• Increased draw distances
• Higher quality global illumination
• Improved day and night lighting
• Enhanced reflections and shadows
• Improved grass and fur textures

System Requirements:
• OS: Windows 10/11
• CPU: Intel Core i7-4770K / AMD Ryzen 5 1500X
• RAM: 12 GB
• GPU: NVIDIA GeForce GTX 1060 6GB / AMD Radeon RX 480 4GB
• Storage: 125 GB""",
        "genre": ["Action", "Adventure", "Open World"],
        "developer": "Rockstar Games",
        "download_links": {
            "filecrypt": "https://filecrypt.co/Container/36B74740A6",
            "1fichier": "https://1fichier.com/?4lsjxts49wcetrq4oq4w"
        }
    },
    {
        "id": "cyberpunk-2077",
        "name": "Cyberpunk 2077",
        "category": "Games",
        "version": "v2.2 + Phantom Liberty",
        "size": "85 GB",
        "date_added": "2024-12-20",
        "downloads": random.randint(2000, 4000),
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
        "screenshots": [
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/ss_b529b0abc43f55fc23fe8058eddb6e37c9629a6a.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/ss_872822c5e50dc71f345416098d29fc3ae5cd26c4.jpg",
            "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/ss_6cef0f72c1918c3a3c3c10b3541f30978cae8a49.jpg"
        ],
        "description": """Cyberpunk 2077 is an action-adventure set in Night City, where you play as a cyberpunk mercenary fighting for survival. Improved with all-new free extra content, you can now personalize your character and playstyle as you take on jobs, establish a reputation, and acquire improvements.

Features:
• Update 2.1 with NCART metro system
• Fully functional Radioport for music
• Enhanced bike combat and handling
• Partner interactions at V's apartment
• Replayable races and new vehicles
• Hidden secrets and more

Includes:
• Base Game + Update 2.2
• Phantom Liberty DLC
• REDmod Support
• Bonus Content Pack

System Requirements:
• OS: Windows 10/11
• CPU: Intel Core i7-6700 / AMD Ryzen 5 1600
• RAM: 16 GB
• GPU: NVIDIA GeForce GTX 1060 6GB / AMD Radeon RX 580 8GB
• Storage: 85 GB""",
        "genre": ["Action", "Adventure", "Role-playing", "Sci-fi"],
        "developer": "CD PROJEKT RED",
        "download_links": {
            "filecrypt": "https://www.filecrypt.cc/Container/DC537CF038.html",
            "datanodes": "https://datanodes.to/axiexhdogrb6/Cbpunk-2ksevenseven-SteamRIP.com.rar",
            "buzzheavier": "https://buzzheavier.com/sdiw114yxgkz",
            "1fichier": "https://1fichier.com/?u3czwon2p536woe1nppl"
        }
    },
    {
        "id": "spiderman-remastered",
        "name": "Marvel's Spider-Man Remastered",
        "version": "Latest Version",
        "size": "75 GB",
        "category": "Games",
        "description": """Marvel's Spider-Man Remastered for PC brings an experienced Peter Parker fighting crime and iconic villains in Marvel's New York. Key features include:

• Be Greater: When iconic Marvel villains threaten Marvel's New York, Peter Parker and Spider-Man's worlds collide.
• Feel like Spider-Man: Experience improvisational combat, dynamic acrobatics, fluid urban traversal, and environmental interactions.
• Worlds Collide: Original action-packed story with reimagined iconic characters from Peter and Spider-Man's lives.
• Marvel's New York: Swing through vibrant neighborhoods, catch breathtaking views of Manhattan landmarks, and use the environment for epic takedowns.
• Complete Content: Includes The City That Never Sleeps DLC with additional missions and challenges.""",
        "genre": ["Action", "Adventure", "Open World"],
        "developer": "Insomniac Games",
        "downloads": "1850",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1817070/header.jpg",
        "download_links": {
            "filecrypt": "https://filecrypt.co/Container/E6F526A6CF",
            "buzzheavier": "https://buzzheavier.com/716go6imtzta",
            "megadb": "https://megadb.net/aajy6i7oy9ot",
            "1fichier": "https://1fichier.com/?tjy8f0ybk66ojeur0sv3"
        }
    },
]

# Initialize the software list and download counts
software_list = SAMPLE_SOFTWARE.copy()
download_counts = {s['id']: s['downloads'] for s in software_list}

@app.route('/')
def home():
    return render_template('index.html', software_list=software_list)

@app.route('/category/<category>')
def category(category):
    filtered_software = [s for s in software_list if s['category'].lower() == category.lower()]
    return render_template('index.html', software_list=filtered_software, category=category)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({'redirect': '/'})
    matching_software = []
    for software in software_list:
        if (query in software['name'].lower() or
            query in software.get('description', '').lower() or
            query in software.get('category', '').lower()):
            matching_software.append(software)
    return render_template('index.html', 
                         software_list=matching_software,
                         search_query=query)

@app.route('/download/<software_id>')
def download(software_id):
    software = next((s for s in software_list if s['id'] == software_id), None)
    
    if software is None:
        return jsonify({'error': 'Software not found'}), 404
    
    # Increment download count
    download_counts[software_id] = download_counts.get(software_id, 0) + 1
    software['downloads'] = download_counts[software_id]
    
    # Get the download URL based on priority
    download_links = software.get('download_links', {})
    
    # Priority order for download links
    link_types = ['filecrypt', 'mega', 'gdrive', '1fichier', 'buzzheavier', 'megadb', 'official']
    
    for link_type in link_types:
        if link_type in download_links:
            return redirect(download_links[link_type])
    
    # Fallback to external_url if available
    if 'external_url' in software:
        return redirect(software['external_url'])
    
    return jsonify({'error': 'No download URL available'}), 404

if __name__ == '__main__':
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    # In production, debug should be False
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
