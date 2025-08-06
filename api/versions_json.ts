export type StringUrl = string;
export type Phase = "alpha" | "beta" | "release-canadate" | "release";
export type PseudoPhase = Phase | "*";
export type VersionId = string;

export type VersionInfo = {
  "epoch": number,
  "date": string,
  "id": VersionId,
  "phase": Phase,
  "maven-jitpack": string | undefined,
  "maven-central": string | undefined,
  "dependencies": StringUrl | undefined
}

export type LoaderCoreVersionsJson = {
  "latest": Record<PseudoPhase, VersionId>,
  "existing-phases": Phase[],
  "versions": Record<VersionId, VersionInfo>
}

export function getVersionDataAsync(url: string): Promise<LoaderCoreVersionsJson|undefined> {
  const dataGet = async () => {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const json = await response.json();
      const data = json as LoaderCoreVersionsJson;
      return data;
    } catch (error) {
      console.error(error);
      return undefined
    }
  }
  return dataGet()
}

export function getVersionDataImmediate(url: string): LoaderCoreVersionsJson|undefined {
  try {
    const xhr = new XMLHttpRequest()

    xhr.overrideMimeType('text/plain; charset=x-user-defined') 
    xhr.open('GET', url, false)
    xhr.send()

    const uint8 = Uint8Array.from(xhr.response, (c:any) => c.charCodeAt(0))
    const text = new TextDecoder().decode(uint8)
    const json = JSON.parse(text)

    return json as LoaderCoreVersionsJson
  } catch(e) {
    return undefined
  }
}