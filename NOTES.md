# Holodeck Architecture Overview

## System Architecture Diagram

```mermaid
graph LR
    subgraph "User Interface Layer"
        CLI[Command Line Interface<br/>main.py]
        Unity[Unity Visualization<br/>connect_to_unity.py]
    end

    subgraph "Core Generation Engine"
        Holodeck[Holodeck Core<br/>holodeck.py]
        ObjectSelector[Object Selector<br/>object_selector.py]
        ObjathorRetriever[Asset Retriever<br/>objaverse_retriever.py]
    end

    subgraph "Language Models & AI"
        OpenAI[OpenAI GPT-4o<br/>Language Generation]
        CLIP[CLIP Model<br/>Visual-Text Matching]
        SBERT[Sentence Transformer<br/>Text Embeddings]
    end

    subgraph "Scene Generation Components"
        FloorPlanGen[Floor Plan Generator<br/>rooms.py]
        WallGen[Wall Generator<br/>walls.py]
        FloorObjGen[Floor Object Generator<br/>floor_objects.py]
        WallObjGen[Wall Object Generator<br/>wall_objects.py]
        SmallObjGen[Small Object Generator<br/>small_objects.py]
        CeilingObjGen[Ceiling Object Generator<br/>ceiling_objects.py]
        DoorGen[Door Generator<br/>doors.py]
        WindowGen[Window Generator<br/>windows.py]
        LightGen[Light Generator<br/>lights.py]
        SkyboxGen[Skybox Generator<br/>skybox.py]
    end

    subgraph "Constraint Solving"
        DFS_Floor[DFS Floor Solver<br/>floor_objects.py]
        DFS_Wall[DFS Wall Solver<br/>wall_objects.py]
        MILP[MILP Solver<br/>milp_utils.py]
    end

    subgraph "Data Sources"
        ObjathorAssets[Objathor Assets<br/>3D Object Database]
        ThorAssets[AI2-THOR Assets<br/>Scene Components]
        Annotations[Object Annotations<br/>Metadata & Features]
    end

    subgraph "Output & Visualization"
        SceneJSON[Scene JSON<br/>3D Scene Description]
        Images[Generated Images<br/>Top-down Views]
        Videos[Generated Videos<br/>Scene Walkthroughs]
        AI2THOR[AI2-THOR Engine<br/>3D Rendering]
    end

    CLI --> Holodeck
    Holodeck --> ObjectSelector
    Holodeck --> FloorPlanGen
    
    ObjectSelector --> ObjathorRetriever
    ObjectSelector --> OpenAI
    FloorPlanGen --> OpenAI
    
    ObjathorRetriever --> CLIP
    ObjathorRetriever --> SBERT
    ObjathorRetriever --> ObjathorAssets
    ObjathorRetriever --> Annotations
    
    Holodeck --> WallGen
    Holodeck --> FloorObjGen
    Holodeck --> WallObjGen
    Holodeck --> SmallObjGen
    Holodeck --> CeilingObjGen
    Holodeck --> DoorGen
    Holodeck --> WindowGen
    Holodeck --> LightGen
    Holodeck --> SkyboxGen
    
    FloorObjGen --> DFS_Floor
    WallObjGen --> DFS_Wall
    ObjectSelector --> MILP
    
    WallGen --> ThorAssets
    FloorObjGen --> ObjathorAssets
    WallObjGen --> ObjathorAssets
    SmallObjGen --> ObjathorAssets
    CeilingObjGen --> ObjathorAssets
    
    Holodeck --> SceneJSON
    Holodeck --> Images
    Holodeck --> Videos
    
    SceneJSON --> Unity
    Unity --> AI2THOR
    
    AI2THOR --> AI2THOR

    style Holodeck fill:#e1f5fe,font-size:14px
    style OpenAI fill:#fff3e0,font-size:12px
    style CLIP fill:#fff3e0,font-size:12px
    style SBERT fill:#fff3e0,font-size:12px
    style ObjathorAssets fill:#f3e5f5,font-size:12px
    style ThorAssets fill:#f3e5f5,font-size:12px
    style AI2THOR fill:#e8f5e8,font-size:12px
```

## Architecture Overview

The Holodeck system is a language-guided 3D embodied AI environment generation platform with the following key architectural layers:

### 1. **User Interface Layer**
- **Command Line Interface**: Entry point for scene generation (`main.py`)
- **Unity Visualization**: Connects generated scenes to Unity for 3D visualization (`connect_to_unity.py`)

### 2. **Core Generation Engine**
- **Holodeck Core**: Main orchestrator that coordinates the entire generation pipeline
- **Object Selector**: Intelligent selection and placement of objects using constraint solving
- **Asset Retriever**: Retrieves and matches 3D assets from object databases

### 3. **Language Models & AI**
- **OpenAI GPT-4o**: Generates floor plans, object lists, and scene descriptions from natural language
- **CLIP Model**: Matches text descriptions to visual assets for object retrieval
- **Sentence Transformer**: Creates embeddings for semantic similarity matching

### 4. **Scene Generation Components**
A modular set of specialized generators for different scene elements:
- **Floor Plan Generator**: Creates room layouts from text descriptions
- **Wall/Floor/Ceiling Generators**: Generate structural elements
- **Object Generators**: Place furniture, decorations, and interactive objects
- **Door/Window Generators**: Add architectural features
- **Lighting/Skybox**: Handle environmental elements

### 5. **Constraint Solving**
- **DFS Solvers**: Depth-first search algorithms for object placement optimization
- **MILP Solver**: Mixed Integer Linear Programming for complex spatial constraints

### 6. **Data Sources**
- **Objathor Assets**: Large database of 3D objects with metadata
- **AI2-THOR Assets**: Scene components and materials
- **Annotations**: Rich metadata for object properties and relationships

### 7. **Output & Visualization**
- **Scene JSON**: Structured 3D scene descriptions
- **Generated Media**: Images and videos of created environments
- **AI2-THOR Integration**: Real-time 3D rendering and interaction

The system transforms natural language descriptions (e.g., "a cozy living room") into fully realized 3D environments through a sophisticated pipeline that combines large language models, computer vision, constraint solving, and 3D graphics.
