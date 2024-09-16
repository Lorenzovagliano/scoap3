import React, { useEffect, useState, useCallback } from "react";
import { XYPlot, VerticalBarSeries, Hint } from "react-vis";
import { Button, Card, Slider } from "antd";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import "react-vis/dist/style.css";

import { PublicationYear, YearFacetData } from "@/types";


const mapInitialDataToYears = (
  initial: PublicationYear[]
): YearFacetData[] => {
  return initial?.map((item) => ({
    x: new Date(item?.key)?.getFullYear(),
    y: item?.doc_count,
  }));
};

const YearFacet = ({ data }: any) => {
  const [hoveredBar, setHoveredBar] = useState<any>(null);
  const [filters, setFilters] = useState<YearFacetData[]>([]);
  const [initialEndpoints, setInitialEndpoints] = useState<number[]>([]);
  const [sliderEndpoints, setSliderEndpoints] = useState<number[]>([]);

  const router = useRouter();
  const pathname = usePathname()
  const searchParams = useSearchParams();

  useEffect(() => {
    const initialData = mapInitialDataToYears(data);
    setFilters(initialData);
    setSliderEndpoints(getSliderEndpoints(initialData));
    setInitialEndpoints(getSliderEndpoints(initialData));
  }, [data]);

  const resolveYearQuery = (range: number[]) => {
    if (range[0] === range[1]) {
      return range[0]?.toString();
    }
    return range.join("__");
  };

  const createQueryString = useCallback(
    (name: string, value: any) => {
      const params = new URLSearchParams(searchParams.toString())

      params.delete(name);
      params.delete("page");
      params.set(name, resolveYearQuery([value[0].x, value[1].x]));

      return params.toString()
    },
    [searchParams]
  )

  const getSliderEndpoints = (initial: YearFacetData[]): number[] => {
    if (initial.length === 1) return [initial[0]?.x];
    return [initial[0]?.x, initial[initial.length - 1]?.x];
  };

  const onSliderChange = (data: number[]) => {
    setSliderEndpoints(data)
  };

  const onSliderAfterChange = (data: number[]) => {
    setSliderEndpoints(data)
    const params = createQueryString('publication_year__range',  [{x:data[0]}, {x:data[1]}]);
    router.push(pathname + (params ? `?${params.toString()}` : ""))
  };

  const onBarClick = (value: YearFacetData) => {
    const params = createQueryString('publication_year__range', [value, value]);
    router.push(pathname + (params ? `?${params.toString()}` : ""))
  };

  const onBarMouseHover = (bar: YearFacetData) => {
    setHoveredBar({ [bar.x]: bar.y });
  };

  const onBarMouseOut = () => setHoveredBar(null);

  const resetFilters = () => {
    const params = new URLSearchParams(searchParams.toString());
    params.delete('publication_year__range');
    params.delete('page');
    router.push(pathname + (params.toString() ? `?${params.toString()}` : ""))
  };

  let marks: any = {}
  filters.map(
    (i, idx) => {
      marks[`${i.x}`] = {
        label: idx == 0 || idx == filters.length-1 ? `${i.x}` : ` `
      };
    }
  );

  return (
    <Card title="Year" className="search-facets-facet mb-5">
      <div>
        {searchParams.get('publication_year__range') && (
          <div className="text-right mb-3">
            <Button
              onClick={resetFilters}
              className="ml-1"
              type="primary"
              size="small"
            >
              Reset
            </Button>
          </div>
        )}
        <XYPlot
          height={80}
          width={150}
          margin={0}
          className="year-facet"
        >
          {hoveredBar && <Hint value={hoveredBar} />}
          <VerticalBarSeries
            className="current-data"
            color="#3498db"
            data={filters}
            onValueClick={onBarClick}
            onValueMouseOver={onBarMouseHover}
            onValueMouseOut={onBarMouseOut}
            barWidth={0.5}
          />
        </XYPlot>
      </div>
      <Slider
        range
        disabled={Object.keys(marks).length <= 1 }
        step={null}
        className="year-facet-slider"
        onChange={onSliderChange}
        onAfterChange={onSliderAfterChange}
        value={sliderEndpoints}
        defaultValue={initialEndpoints}
        min={initialEndpoints[0]}
        max={initialEndpoints[1]}
        marks={marks}
      />
    </Card>
  );
};

export default YearFacet;
