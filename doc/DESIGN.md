# 4-Panel Manga Generator 設計仕様書

## 1. 概要

Google Gemini API (`gemini-3-pro-image-preview`) を使用して、4コマ漫画を生成するWebアプリケーション。

## 2. システムアーキテクチャ

### 2.1 構成図

```
[Browser] <-> [FastAPI Server] <-> [Google Gemini API]
                      |
                [Static Files]
                [Reference Images]
                [Output Images]
```

### 2.2 主要コンポーネント

- **FastAPIサーバー**: REST API提供、静的ファイル配信
- **Gemini API Client**: 画像生成処理
- **Frontend (Vanilla JS)**: ユーザーインターフェース

## 3. Gemini API統合仕様

### 3.1 APIクライアント初期化

```python
from google import genai
from google.genai import types
import os

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)
```

### 3.2 モデル仕様

- **モデル名**: `gemini-3-pro-image-preview`
- **レスポンスモダリティ**: `["IMAGE", "TEXT"]`
- **画像設定**:
  - `aspect_ratio`: ユーザー指定 (例: "3:4", "1:1", "16:9")
  - `image_size`: "2K" (固定)
  - `person_generation`: "" (空文字列)

### 3.3 コンテンツ構造

#### 3.3.1 リクエストコンテンツの構成

```python
contents = [
    types.Content(
        role="user",
        parts=[
            # テキストプロンプト
            types.Part.from_text(text=prompt_text),

            # レイアウトリファレンス画像（オプション）
            types.Part.from_bytes(
                data=layout_image_bytes,
                mime_type="image/png"  # または "image/jpeg"
            ),

            # キャラクターリファレンス画像（複数可）
            types.Part.from_bytes(
                data=char1_image_bytes,
                mime_type="image/png"
            ),
            # ... 他のキャラクター
        ]
    )
]
```

#### 3.3.2 GenerateContentConfig

```python
generate_content_config = types.GenerateContentConfig(
    image_config=types.ImageConfig(
        aspect_ratio=aspect_ratio,  # ユーザー指定値
        image_size="2K",
        person_generation=""
    ),
    response_modalities=["IMAGE", "TEXT"]
)
```

### 3.4 ストリーミングレスポンス処理

```python
file_index = 0
thought_process = []

for chunk in client.models.generate_content_stream(
    model="gemini-3-pro-image-preview",
    contents=contents,
    config=generate_content_config
):
    if chunk.parts is None:
        continue

    # 画像データの処理
    if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
        inline_data = chunk.parts[0].inline_data
        data_buffer = inline_data.data

        # MIMEタイプから拡張子を取得
        file_extension = mimetypes.guess_extension(inline_data.mime_type)

        # ファイル保存
        file_name = f"manga_panel_{timestamp}_{file_index}{file_extension}"
        save_path = f"static/outputs/{file_name}"
        save_binary_file(save_path, data_buffer)

        file_index += 1

    # テキスト（思考過程）の処理
    else:
        thought_process.append(chunk.text)
```

### 3.5 画像ファイルの保存

```python
def save_binary_file(file_path: str, data: bytes) -> None:
    """バイナリデータをファイルに保存

    Args:
        file_path: 保存先パス
        data: バイナリデータ
    """
    with open(file_path, "wb") as f:
        f.write(data)
```

## 4. プロンプト設計

### 4.1 プロンプト構造

4コマ漫画生成のためのプロンプトは以下の構造を持つ：

```markdown
# 4-Panel Manga Generation Request

## Overall Instructions
Generate a 4-panel manga based on the following specifications.

## Character References
{character_count} character(s) are provided as reference images.

{for each character}
### Character {index}: {name}
- Reference image provided
- Description: {description if any}
{end for}

## Layout Reference
{if layout_ref exists}
A layout reference image is provided showing the desired panel arrangement.
{end if}

## Panel Specifications

### Panel 1: {scene_title}
**Scene:** {scene_description}

**Characters:**
{for each character}
- {character_name}: {character_state}
{end for}

**Background & Objects:** {objects_background}

---

### Panel 2: {scene_title}
...

---

### Panel 3: {scene_title}
...

---

### Panel 4: {scene_title}
...

## Output Requirements
- Generate a single image containing all 4 panels
- Follow the layout reference if provided
- Maintain character consistency across panels
- Use the specified aspect ratio
```

### 4.2 プロンプト生成関数

```python
def build_manga_prompt(
    characters: List[CharacterInput],
    scenes: List[SceneInput],
    has_layout_ref: bool
) -> str:
    """4コマ漫画生成用のプロンプトを構築

    Args:
        characters: キャラクター情報のリスト
        scenes: 4つのシーン情報
        has_layout_ref: レイアウトリファレンスの有無

    Returns:
        構造化されたプロンプト文字列
    """
    prompt_parts = []

    # ヘッダー
    prompt_parts.append("# 4-Panel Manga Generation Request\n")
    prompt_parts.append("## Overall Instructions")
    prompt_parts.append("Generate a 4-panel manga based on the following specifications.\n")

    # キャラクター情報
    if characters:
        prompt_parts.append(f"## Character References")
        prompt_parts.append(f"{len(characters)} character(s) are provided as reference images.\n")

        for idx, char in enumerate(characters, 1):
            prompt_parts.append(f"### Character {idx}: {char.name}")
            prompt_parts.append("- Reference image provided")
            if char.description:
                prompt_parts.append(f"- Description: {char.description}")
            prompt_parts.append("")

    # レイアウトリファレンス
    if has_layout_ref:
        prompt_parts.append("## Layout Reference")
        prompt_parts.append("A layout reference image is provided showing the desired panel arrangement.\n")

    # パネル仕様
    prompt_parts.append("## Panel Specifications\n")

    for idx, scene in enumerate(scenes, 1):
        prompt_parts.append(f"### Panel {idx}")
        prompt_parts.append(f"**Scene:** {scene.scene_description}\n")

        if scene.character_states:
            prompt_parts.append("**Characters:**")
            for char_id, state in scene.character_states.items():
                char_name = next(
                    (c.name for c in characters if str(c.id) == str(char_id)),
                    f"Character {char_id}"
                )
                prompt_parts.append(f"- {char_name}: {state}")
            prompt_parts.append("")

        if scene.objects_background:
            prompt_parts.append(f"**Background & Objects:** {scene.objects_background}\n")

        prompt_parts.append("---\n")

    # 出力要件
    prompt_parts.append("## Output Requirements")
    prompt_parts.append("- Generate a single image containing all 4 panels")
    if has_layout_ref:
        prompt_parts.append("- Follow the layout reference if provided")
    prompt_parts.append("- Maintain character consistency across panels")
    prompt_parts.append("- Use manga/comic art style")

    return "\n".join(prompt_parts)
```

## 5. 画像処理

### 5.1 リファレンス画像の読み込み

```python
def load_image_bytes(file_path: str) -> tuple[bytes, str]:
    """画像ファイルをバイナリとして読み込む

    Args:
        file_path: 画像ファイルパス

    Returns:
        (バイナリデータ, MIMEタイプ)のタプル
    """
    with open(file_path, "rb") as f:
        data = f.read()

    mime_type = get_mime_type(file_path)
    return data, mime_type
```

### 5.2 アップロード画像の処理

```python
from fastapi import UploadFile

async def save_uploaded_file(
    file: UploadFile,
    directory: str
) -> str:
    """アップロードされた画像を保存

    Args:
        file: アップロードファイル
        directory: 保存先ディレクトリ

    Returns:
        保存されたファイル名
    """
    # ファイル名のサニタイズ
    safe_filename = secure_filename(file.filename)

    # ユニークなファイル名生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{safe_filename}"

    file_path = Path(directory) / unique_filename

    # ファイル保存
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return unique_filename
```

## 6. API エンドポイント実装

### 6.1 画像生成エンドポイント

```python
@app.post("/api/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """4コマ漫画を生成"""

    try:
        settings = get_settings()
        validate_api_key(settings.gemini_api_key)

        # Gemini クライアント初期化
        client = genai.Client(api_key=settings.gemini_api_key)

        # プロンプト構築
        prompt_text = build_manga_prompt(
            characters=request.characters,
            scenes=request.scenes,
            has_layout_ref=bool(request.layout_ref_image)
        )

        # コンテンツパーツの構築
        parts = [types.Part.from_text(text=prompt_text)]

        # レイアウトリファレンス画像の追加
        if request.layout_ref_image:
            layout_path = f"static/layout_refs/{request.layout_ref_image}"
            if Path(layout_path).exists():
                image_data, mime_type = load_image_bytes(layout_path)
                parts.append(types.Part.from_bytes(
                    data=image_data,
                    mime_type=mime_type
                ))

        # キャラクターリファレンス画像の追加
        for char in request.characters:
            if char.ref_image:
                char_path = f"static/char_refs/{char.ref_image}"
                if Path(char_path).exists():
                    image_data, mime_type = load_image_bytes(char_path)
                    parts.append(types.Part.from_bytes(
                        data=image_data,
                        mime_type=mime_type
                    ))

        # コンテンツ構築
        contents = [types.Content(role="user", parts=parts)]

        # 設定
        config = types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio=request.aspect_ratio,
                image_size="2K",
                person_generation=""
            ),
            response_modalities=["IMAGE", "TEXT"]
        )

        # ストリーミング生成
        thought_process_parts = []
        generated_image_url = None
        file_index = 0
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for chunk in client.models.generate_content_stream(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=config
        ):
            if chunk.parts is None:
                continue

            # 画像データの処理
            if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
                inline_data = chunk.parts[0].inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)

                file_name = f"manga_{timestamp}_{file_index}{file_extension}"
                file_path = f"static/outputs/{file_name}"

                save_binary_file(file_path, data_buffer)
                generated_image_url = f"/static/outputs/{file_name}"
                file_index += 1

            # テキスト（思考過程）の処理
            else:
                thought_process_parts.append(chunk.text)

        # レスポンス構築
        return ImageGenerationResponse(
            success=True,
            thought_process="".join(thought_process_parts),
            image_url=generated_image_url,
            error=None
        )

    except Exception as e:
        return ImageGenerationResponse(
            success=False,
            thought_process="",
            image_url=None,
            error=str(e)
        )
```

### 6.2 ファイルアップロードエンドポイント

```python
@app.post("/api/upload/layout")
async def upload_layout(file: UploadFile = File(...)):
    """レイアウトリファレンス画像をアップロード"""
    try:
        filename = await save_uploaded_file(file, "static/layout_refs")
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/character")
async def upload_character(file: UploadFile = File(...)):
    """キャラクターリファレンス画像をアップロード"""
    try:
        filename = await save_uploaded_file(file, "static/char_refs")
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 7. エラーハンドリング

### 7.1 API エラー

```python
class GeminiAPIError(Exception):
    """Gemini API関連のエラー"""
    pass

def handle_gemini_error(error: Exception) -> str:
    """Gemini APIエラーをユーザーフレンドリーなメッセージに変換"""
    error_msg = str(error)

    if "API_KEY" in error_msg:
        return "API key is invalid or not configured"
    elif "RATE_LIMIT" in error_msg:
        return "Rate limit exceeded. Please try again later"
    elif "QUOTA" in error_msg:
        return "API quota exceeded"
    else:
        return f"Image generation failed: {error_msg}"
```

### 7.2 バリデーションエラー

- Pydanticモデルによる自動バリデーション
- カスタムバリデーター（`@field_validator`）での追加チェック
- 適切なHTTPステータスコード（400, 500）の返却

## 8. セキュリティ考慮事項

### 8.1 入力バリデーション

- ファイル名のサニタイズ
- ファイルサイズ制限（推奨: 10MB）
- 許可する画像形式の制限（PNG, JPEG, WebP）
- プロンプトの最大長制限

### 8.2 API キーの保護

- 環境変数からの読み込み
- `.env`ファイルの`.gitignore`への追加
- フロントエンドへのAPI keyの露出禁止

### 8.3 ファイルシステムセキュリティ

- パストラバーサル攻撃の防止
- アップロードファイルの検証
- 出力ディレクトリのアクセス制限

## 9. パフォーマンス最適化

### 9.1 画像処理

- 適切な画像サイズへのリサイズ
- 画像圧縮の適用
- キャッシュの活用

### 9.2 API呼び出し

- タイムアウト設定
- リトライロジック（エクスポネンシャルバックオフ）
- レート制限の遵守

## 10. リトライ機能実装

### 10.1 思考過程からやり直し

通常の生成処理と同じフローを実行。

### 10.2 画像生成のみやり直し

```python
@app.post("/api/regenerate-image")
async def regenerate_image(
    request: RegenerateImageRequest
):
    """前回の思考過程を使用して画像のみ再生成

    Args:
        request.thought_process: 前回生成された思考過程
        request.aspect_ratio: アスペクト比
    """
    # 思考過程をプロンプトとして使用
    parts = [types.Part.from_text(text=request.thought_process)]

    # 同じ設定で画像のみ生成
    # （思考過程はスキップされ、画像生成に直接進む）
    ...
```

## 11. テスト戦略

### 11.1 ユニットテスト

- `utils.py`の各関数
- プロンプト生成ロジック
- バリデーション機能

### 11.2 統合テスト

- APIエンドポイント
- ファイルアップロード
- 画像生成フロー

### 11.3 E2Eテスト

- フロントエンドからバックエンドまでのフルフロー
- エラーケースの処理
- リトライ機能

## 12. デプロイメント

### 12.1 環境変数

```bash
GEMINI_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 12.2 依存関係

- Python 3.10以上
- 必要なディレクトリ構造の自動作成
- ログ設定

### 12.3 本番環境での考慮事項

- HTTPSの使用
- CORS設定の適切な制限
- ログの適切な管理
- エラートラッキング
- メトリクス収集
