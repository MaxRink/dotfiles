# compare-versions.jq - jq filter for comparing bundle versions
# Usage: jq -n --arg b1 "bundle1" --arg b2 "bundle2" --argjson j1 'json1' --argjson j2 'json2' -f compare-versions.jq

# Build lookup maps keyed by "function|component"
(($j1.components // [])
  | map(select(.component != null and .component != ""))
  | map({key: "\(.function // "unknown")|\(.component)", value: .})
  | from_entries) as $map1 |

(($j2.components // [])
  | map(select(.component != null and .component != ""))
  | map({key: "\(.function // "unknown")|\(.component)", value: .})
  | from_entries) as $map2 |

# Get all unique keys (combine the key arrays, then unique)
((($map1 | keys) + ($map2 | keys)) | unique) as $all_keys |

# Build comparison results
{
    bundle1: $b1,
    bundle2: $b2,
    comparisons: [
        $all_keys[] | . as $key |
        ($map1[$key] // null) as $v1 |
        ($map2[$key] // null) as $v2 |
        {
            function: ($v1.function // $v2.function // ($key | split("|")[0])),
            component: ($v1.component // $v2.component // ($key | split("|")[1])),
            type_version1: (($v1.type_version // "-") | tostring),
            type_version2: (($v2.type_version // "-") | tostring),
            image_version1: (($v1.image_version // "-") | tostring),
            image_version2: (($v2.image_version // "-") | tostring),
            status: (
                if ($v1 == null) then "added"
                elif ($v2 == null) then "removed"
                elif (($v1.image_version // "") == ($v2.image_version // "")) then "same"
                else "changed"
                end
            )
        }
    ] | sort_by(.function)
}
